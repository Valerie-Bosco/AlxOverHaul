$parent_directory = Split-Path -Path (Get-Location) -Leaf -Resolve
$target_subfolder = Split-Path -Path ".\$parent_directory" -Leaf -Resolve

if ( Test-Path ".\$target_subfolder\__pycache__" )
{
    Remove-Item  -Recurse -Path ".\$target_subfolder\__pycache__"
}
if ( Test-Path ".\$target_subfolder\alxoverhaul_updater" )
{
    Remove-Item  -Recurse -Path ".\$target_subfolder\alxoverhaul_updater"
}
if ( Test-Path ".\$target_subfolder")
{
    Compress-Archive -Force -Path .\$target_subfolder -Destination ".\$target_subfolder.zip"
} 