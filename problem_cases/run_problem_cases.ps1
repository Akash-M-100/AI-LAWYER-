$ErrorActionPreference = 'Stop'
$repoDir = Split-Path -Parent $PSScriptRoot
$parentDir = Split-Path -Parent $repoDir
$projectDir = $repoDir
if ((Test-Path -LiteralPath (Join-Path $parentDir '.env')) -and
    (Test-Path -LiteralPath (Join-Path $parentDir 'chroma_db')) -and
    (Test-Path -LiteralPath (Join-Path $parentDir 'agent.py'))) {
    # In the shared workspace, prefer the configured project beside the clone.
    $projectDir = $parentDir
}
$agentFile = Join-Path $projectDir 'agent.py'
$python = Join-Path $projectDir '.venv\Scripts\python.exe'
$pythonArguments = @()

if (-not (Test-Path -LiteralPath $python)) {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand) {
        $python = $pythonCommand.Source
    } else {
        $launcher = Get-Command py -ErrorAction SilentlyContinue
        if (-not $launcher) {
            throw 'Python was not found. Activate the project virtual environment or install Python, then rerun.'
        }
        $python = $launcher.Source
        $pythonArguments = @('-3.11')
    }
}

$outputRoot = Join-Path $PSScriptRoot 'outputs'
$runId = Get-Date -Format 'yyyyMMdd_HHmmss'
$runDir = Join-Path $outputRoot ('run_' + $runId)
$null = New-Item -ItemType Directory -Path $runDir -Force

$caseFiles = Get-ChildItem -LiteralPath $PSScriptRoot -Filter '*.md' -File |
    Where-Object { $_.Name -match '^\d{2}_' } |
    Sort-Object Name

foreach ($caseFile in $caseFiles) {
    $caseText = Get-Content -LiteralPath $caseFile.FullName -Raw
    $promptBlock = [regex]::Match(
        $caseText,
        '(?ms)^## First message to the assistant\s*\r?\n(.*?)(?=^## )'
    )
    if (-not $promptBlock.Success) {
        throw "Could not find the first-message prompt in $($caseFile.Name)."
    }

    $question = ($promptBlock.Groups[1].Value -split '\r?\n' |
        Where-Object { $_ -match '^[ \t]*>[ \t]?' } |
        ForEach-Object { $_ -replace '^[ \t]*>[ \t]?', '' }) -join "`n"
    if ([string]::IsNullOrWhiteSpace($question)) {
        throw "The first-message prompt is empty in $($caseFile.Name)."
    }

    $outputFile = Join-Path $runDir ($caseFile.BaseName + '_raw.txt')
    @($question, 'exit') | & $python @pythonArguments $agentFile 2>&1 |
        Out-File -LiteralPath $outputFile -Encoding utf8
    Write-Output "Saved bot transcript: $outputFile"
}

Write-Output "Completed run: $runDir"
