param(
    [switch]$Build,
    [int]$Port = 5173
)

$ErrorActionPreference = "Stop"

Push-Location frontend
try {
    if ($Build) {
        node .\node_modules\typescript\bin\tsc -b
        node .\node_modules\vite\bin\vite.js build
    } else {
        node .\node_modules\vite\bin\vite.js --host localhost --port $Port
    }
} finally {
    Pop-Location
}
