# agendar_digest.ps1
# Agenda o digest semanal para toda sexta-feira às 17h
# Execute como Administrador

$scriptDir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonPath = "C:\Program Files\Python313\python.exe"
$scriptPath = Join-Path $scriptDir "pipeline.py"

$action   = New-ScheduledTaskAction -Execute $pythonPath -Argument "`"$scriptPath`" --digest" -WorkingDirectory $scriptDir
$trigger  = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Friday -At "17:00"
$settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 10) -StartWhenAvailable

Unregister-ScheduledTask -TaskName "SecondBrainDigest" -Confirm:$false -ErrorAction SilentlyContinue

Register-ScheduledTask `
    -TaskName    "SecondBrainDigest" `
    -Action      $action `
    -Trigger     $trigger `
    -Settings    $settings `
    -Description "Second Brain: digest semanal toda sexta 17h" `
    -RunLevel    Highest

Write-Host ""
Write-Host "Digest agendado: SecondBrainDigest - toda sexta as 17h" -ForegroundColor Green
Write-Host "Para rodar agora: python `"$scriptPath`" --digest"
