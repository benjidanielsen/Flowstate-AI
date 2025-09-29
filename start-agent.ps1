# Start the agent runner in the foreground (interactive)

# Ensure we don't rely on aliases (e.g. 'cd') and use explicit, robust cmdlets.
if (-not $PSScriptRoot) {
    Throw "PSScriptRoot is not set. Run this script from a file context."
}

Set-Location -LiteralPath $PSScriptRoot -ErrorAction Stop

# Build an explicit path to the Python script and invoke Python via the call operator.
$agentScript = Join-Path -Path $PSScriptRoot -ChildPath ".multicoder\task\agent_runner.py"
& python $agentScript --interval 600 --run-tests
