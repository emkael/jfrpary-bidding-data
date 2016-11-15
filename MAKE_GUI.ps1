& pyinstaller bidding_data_gui.spec --distpath dist\gui
Copy-Item '*.md' -Destination 'dist\gui' -Force
Copy-Item 'res\*' -Destination 'dist\gui' -Force -Recurse
Set-Variable -Name VersionInfo -Value (Get-Item 'dist\gui\bidding_data.exe').VersionInfo
Set-Variable -Name FileVersion -Value $VersionInfo.FileVersion.Split(',')
Set-Variable -Name BundleName -Value ('bundle\\' + $VersionInfo.InternalName + '-' + $FileVersion[0].Trim() + '.' + $FileVersion[1].Trim() + '-gui.zip')
Remove-Item $BundleName -ErrorAction SilentlyContinue
Add-Type -Assembly 'System.IO.Compression.FileSystem'
[System.IO.Compression.ZipFile]::CreateFromDirectory('dist\gui', $BundleName)
