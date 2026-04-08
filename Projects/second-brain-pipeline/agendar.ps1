# agendar.ps1 — Second Brain Pipeline v2
# Telegram Daemon: processo continuo polling a cada 2min
# Daily: todo dia 22h | Digest: domingos 20h (inclui RSS)
# Execute com: powershell -ExecutionPolicy Bypass -File agendar.ps1

$scriptDir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonPath = (Get-Command python).Source
$scriptPath = Join-Path $scriptDir "pipeline.py"

if (-not (Test-Path $scriptPath)) {
    Write-Error "pipeline.py nao encontrado em $scriptDir"
    exit 1
}

$defaultSettings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries

# ── Telegram Daemon: processo continuo (polling a cada 2min interno) ────────
$actionTelegram = New-ScheduledTaskAction `
    -Execute $pythonPath `
    -Argument "`"$scriptPath`" --mode telegram-daemon" `
    -WorkingDirectory $scriptDir

$triggerTelegram = New-ScheduledTaskTrigger -AtLogon

$settingsTelegram = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -StartWhenAvailable `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1)

# ── Daily Review: todo dia as 22h ───────────────────────────────────────────
$actionDaily = New-ScheduledTaskAction `
    -Execute $pythonPath `
    -Argument "`"$scriptPath`" --daily" `
    -WorkingDirectory $scriptDir

$triggerDaily = New-ScheduledTaskTrigger -Daily -At "22:00"

# ── Digest: domingos as 20h ─────────────────────────────────────────────────
$actionDigest = New-ScheduledTaskAction `
    -Execute $pythonPath `
    -Argument "`"$scriptPath`" --digest" `
    -WorkingDirectory $scriptDir

$triggerDigest = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At "20:00"

# ── Quartz Sync: 2x por dia (7h e 22:30) ───────────────────────────────────
$syncPath = Join-Path $scriptDir "sync_quartz.ps1"
$actionSync = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-ExecutionPolicy Bypass -File `"$syncPath`"" `
    -WorkingDirectory $scriptDir

$triggerSync1 = New-ScheduledTaskTrigger -Daily -At "07:00"
$triggerSync2 = New-ScheduledTaskTrigger -Daily -At "22:30"

# ── Remover tarefas anteriores ───────────────────────────────────────────────
@(
    "SecondBrainPipeline-Manha",
    "SecondBrainPipeline-Tarde",
    "SecondBrainPipeline",
    "SecondBrainTelegram",
    "SecondBrainRSS",
    "SecondBrainDaily",
    "SecondBrainDigest",
    "SecondBrainQuartzSync"
) | ForEach-Object {
    Unregister-ScheduledTask -TaskName $_ -Confirm:$false -ErrorAction SilentlyContinue
}

# ── Criar novas tarefas ─────────────────────────────────────────────────────
Register-ScheduledTask `
    -TaskName    "SecondBrainTelegram" `
    -Action      $actionTelegram `
    -Trigger     $triggerTelegram `
    -Settings    $settingsTelegram `
    -Description "Second Brain: Telegram daemon (polling a cada 2min, inicia no login)" `
    -RunLevel    Highest

Register-ScheduledTask `
    -TaskName    "SecondBrainDaily" `
    -Action      $actionDaily `
    -Trigger     $triggerDaily `
    -Settings    $defaultSettings `
    -Description "Second Brain: review diario (22h)" `
    -RunLevel    Highest

Register-ScheduledTask `
    -TaskName    "SecondBrainDigest" `
    -Action      $actionDigest `
    -Trigger     $triggerDigest `
    -Settings    $defaultSettings `
    -Description "Second Brain: digest semanal (domingos 20h)" `
    -RunLevel    Highest

# Quartz sync (so registra se setup ja foi feito)
if (Test-Path $syncPath) {
    Register-ScheduledTask `
        -TaskName    "SecondBrainQuartzSync" `
        -Action      $actionSync `
        -Trigger     @($triggerSync1, $triggerSync2) `
        -Settings    $defaultSettings `
        -Description "Second Brain: sync Quartz site (7h e 22:30)" `
        -RunLevel    Highest
    Write-Host "   SecondBrainQuartzSync -> 7h e 22:30 (sync site)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Tarefas agendadas:" -ForegroundColor Green
Write-Host "   SecondBrainTelegram  -> daemon continuo (polling 2min, inicia no login)"
Write-Host "   SecondBrainDaily     -> todo dia as 22h"
Write-Host "   SecondBrainDigest    -> domingos as 20h (inclui RSS)"
Write-Host ""
Write-Host "Para verificar:  Get-ScheduledTask -TaskName 'SecondBrain*'"
Write-Host "Testar Telegram: python `"$scriptPath`" --mode telegram"
Write-Host "Daemon manual:   python `"$scriptPath`" --mode telegram-daemon"
Write-Host "Daily manual:    python `"$scriptPath`" --daily"
Write-Host "Testar RSS:      python `"$scriptPath`" --mode rss --dry-run"
