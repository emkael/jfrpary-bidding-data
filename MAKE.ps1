& pyinstaller bidding_data.spec --distpath dist\console
Copy-Item '*.md' -Destination 'dist\console' -Force
Copy-Item 'res\*' -Destination 'dist\console' -Force -Recurse
Set-Variable -Name VersionInfo -Value (Get-Item 'dist\console\bidding_data.exe').VersionInfo
Set-Variable -Name FileVersion -Value $VersionInfo.FileVersion.Split(',')
Set-Variable -Name BundleName -Value ('bundle\\' + $VersionInfo.InternalName + '-' + $FileVersion[0].Trim() + '.' + $FileVersion[1].Trim() + '.zip')
Remove-Item $BundleName -ErrorAction SilentlyContinue
Add-Type -Assembly 'System.IO.Compression.FileSystem'
[System.IO.Compression.ZipFile]::CreateFromDirectory('dist\console', $BundleName)
