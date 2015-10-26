& pyinstaller bidding_data_gui.spec
Copy-Item '*.md' -Destination 'dist' -Force
Copy-Item 'res\*' -Destination 'dist' -Force -Recurse
Set-Variable -Name VersionInfo -Value (Get-Item 'dist\bidding_data.exe').VersionInfo
Set-Variable -Name FileVersion -Value $VersionInfo.FileVersion.Split(',')
Set-Variable -Name BundleName -Value ('bundle\\' + $VersionInfo.InternalName + '-' + $FileVersion[0].Trim() + '.' + $FileVersion[1].Trim() + '-gui.zip')
Remove-Item $BundleName -ErrorAction SilentlyContinue
Add-Type -Assembly 'System.IO.Compression.FileSystem'
[System.IO.Compression.ZipFile]::CreateFromDirectory('dist', $BundleName)
