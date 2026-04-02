# agendar.ps1
# Cria duas tarefas agendadas no Windows: 08:00 e 17:00
# Execute com: powershell -ExecutionPolicy Bypass -File agendar.ps1

$scriptDir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonPath = (Get-Command python).Source
$scriptPath = Join-Path $scriptDir "pipeline.py"

if (-not (Test-Path $scriptPath)) {
    Write-Error "pipeline.py nao encontrado em $scriptDir"
    exit 1
}

$action  = New-ScheduledTaskAction -Execute $pythonPath -Argument "`"$scriptPath`"" -WorkingDirectory $scriptDir
$trigger1 = New-ScheduledTaskTrigger -Daily -At "08:00"
$trigger2 = New-ScheduledTaskTrigger -Daily -At "17:00"
$settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 15) -StartWhenAvailable

# Remove tarefas existentes (se houver)
Unregister-ScheduledTask -TaskName "SecondBrainPipeline-Manha" -Confirm:$false -ErrorAction SilentlyContinue
Unregister-ScheduledTask -TaskName "SecondBrainPipeline-Tarde"  -Confirm:$false -ErrorAction SilentlyContinue

# Cria novas tarefas
Register-ScheduledTask `
    -TaskName    "SecondBrainPipeline-Manha" `
    -Action      $action `
    -Trigger     $trigger1 `
    -Settings    $settings `
    -Description "Second Brain: coleta de feeds matinal" `
    -RunLevel    Highest

Register-ScheduledTask `
    -TaskName    "SecondBrainPipeline-Tarde" `
    -Action      $action `
    -Trigger     $trigger2 `
    -Settings    $settings `
    -Description "Second Brain: coleta de feeds vespertina" `
    -RunLevel    Highest

Write-Host ""
Write-Host "✅ Tarefas agendadas com sucesso:" -ForegroundColor Green
Write-Host "   • SecondBrainPipeline-Manha  → 08:00 todos os dias"
Write-Host "   • SecondBrainPipeline-Tarde  → 17:00 todos os dias"
Write-Host ""
Write-Host "Para verificar: Get-ScheduledTask -TaskName 'SecondBrain*'"
Write-Host "Para rodar agora: python `"$scriptPath`""
