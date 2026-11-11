$ErrorActionPreference = 'Stop'
$submissionDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectDir = Split-Path -Parent $submissionDir
$rawOutputRoot = Join-Path $submissionDir 'raw_outputs'
$runId = Get-Date -Format 'yyyyMMdd_HHmmss'
$outputDir = Join-Path $rawOutputRoot ('run_' + $runId)
$null = New-Item -ItemType Directory -Path $outputDir -Force
$caseFile = Join-Path $submissionDir 'test_cases.json'
$agentFile = Join-Path $projectDir 'agent.py'

$python = Join-Path $projectDir '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCommand) {
        throw 'Python was not found. Create/activate the project virtual environment or install Python, then rerun.'
    }
    $python = $pythonCommand.Source
}

$cases = Get-Content -LiteralPath $caseFile -Raw | ConvertFrom-Json
foreach ($case in $cases) {
    $outputFile = Join-Path $outputDir ($case.id + '.txt')
    $transcript = @($case.question, 'exit') | & $python $agentFile 2>&1
    $transcript | Out-File -LiteralPath $outputFile -Encoding utf8
    Write-Output "Saved $outputFile"
}
