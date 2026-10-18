$ErrorActionPreference = 'Stop'
try {
    $source = Split-Path $PSScriptRoot -Parent
    $target = (Read-Host 'Existing project folder (the one containing your .env)').Trim('"')
    $target = (Resolve-Path -LiteralPath $target).Path
    if (!(Test-Path -LiteralPath (Join-Path $target '.env'))) { throw 'No .env in that folder. Choose the existing running project.' }
    if ($source -eq $target) { throw 'Extract the download to a separate folder, then run this installer again.' }
    $files = @(
        'backend/src/eidolon/app.py',
        'backend/src/eidolon/developer_api.py',
        'backend/src/eidolon/developer_data.py',
        'frontend/src/app/(app)/(nav)/settings/layout.tsx',
        'frontend/src/components/settings/DeveloperSettings.tsx',
        'frontend/src/components/settings/SettingsCategoryPage.tsx',
        'frontend/src/i18n/zh.ts',
        'frontend/src/lib/settingsCategory.ts',
        'docker-compose.yml'
    )
    $backup = Join-Path (Split-Path $target -Parent) ((Split-Path $target -Leaf) + '-devtools-backup-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
    New-Item -ItemType Directory -Path $backup | Out-Null
    foreach ($relative in $files) {
        $destination = Join-Path $target $relative
        if (Test-Path -LiteralPath $destination) {
            $saved = Join-Path $backup $relative
            New-Item -ItemType Directory -Force -Path (Split-Path $saved -Parent) | Out-Null
            Copy-Item -LiteralPath $destination -Destination $saved
        }
    }
    Copy-Item -LiteralPath (Join-Path $target '.env') -Destination (Join-Path $backup '.env')
    Push-Location $target
    try {
        Write-Host 'Users in your current deployment:'
        & docker compose exec -T backend eidolon user list
        if ($LASTEXITCODE -ne 0) { throw 'Could not list users. Start the existing project in Docker first.' }
        $ownerId = (Read-Host 'Paste YOUR user ID from the list (32 hex characters)').Trim()
        if ($ownerId -notmatch '^[a-fA-F0-9]{32}$') { throw 'Invalid user ID; nothing has been installed.' }
        # Verify ownership target exists without using any shell interpolation.
        $check = 'import sqlite3,os,sys; db=sqlite3.connect(os.environ.get("EIDOLON_DATABASE_PATH","data/eidolon.db")); sys.exit(0 if db.execute("SELECT 1 FROM users WHERE id=?",(sys.argv[1],)).fetchone() else 1)'
        $check | & docker compose exec -T backend python - $ownerId
        if ($LASTEXITCODE -ne 0) { throw 'User ID was not found. No files have been installed.' }
        foreach ($relative in $files) {
            $destination = Join-Path $target $relative
            New-Item -ItemType Directory -Force -Path (Split-Path $destination -Parent) | Out-Null
            Copy-Item -LiteralPath (Join-Path $source $relative) -Destination $destination -Force
        }
        $envPath = Join-Path $target '.env'
        $content = [IO.File]::ReadAllText($envPath)
        $line = 'EIDOLON_DEVELOPER_USER=' + $ownerId
        if ($content -match '(?m)^EIDOLON_DEVELOPER_USER=') {
            $content = [regex]::Replace($content, '(?m)^EIDOLON_DEVELOPER_USER=.*$', $line)
        } else { $content = $content.TrimEnd() + "`r`n`r`n" + $line + "`r`n" }
        [IO.File]::WriteAllText($envPath, $content, (New-Object Text.UTF8Encoding($false)))
        & docker compose up -d --build backend frontend
        if ($LASTEXITCODE -ne 0) { throw 'Build failed. See Docker output above; backup is preserved.' }
        Write-Host 'Done. Refresh the website, open Settings > Developer tools / Character sheet.'
        Write-Host ('Original files backed up to: ' + $backup)
    } finally { Pop-Location }
} catch {
    Write-Host ('ERROR: ' + $_.Exception.Message) -ForegroundColor Red
    if ($backup) { Write-Host ('Backup folder: ' + $backup) }
    exit 1
}
