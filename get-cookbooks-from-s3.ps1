# Credits: Based on the bash version in the AWS OpsWorks docs: http://docs.aws.amazon.com/opsworks/latest/userguide/opscm-unattend-assoc.html
# Settings: Change chefServerName and chefServerEndpoint at a minimum

# Required settings
$global:region              = "us-east-1"
$global:computerName	      = $env:ComputerName
$global:chefPath	          = "C:\chef"
$global:cookbooksPath       = $chefPath + "/cookbooks/"
$global:cookbookBucket	    = "snhu-cookbooks"
$global:chefClientVersion          = "stable"

# Recommended: upload the chef-client cookbook from the chef supermarket  https://supermarket.chef.io/cookbooks/chef-client
# Use this to apply sensible default settings for your chef-client configuration like logrotate, and running as a service.
# You can add more cookbooks in the run list, based on your needs

function Install-Chef
{
  $chef_installed = Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* | select DisplayName, Publisher, InstallDate | Where-Object {$_.DisplayName -Like "Chef Client*"}
  if ($chef_installed -eq $null) {
    . { iwr -useb https://omnitruck.chef.io/install.ps1 } | iex; install -channel $chefClientVersion -project chef
  }
}

function Get-WorkspaceId
{
  $workspace_obj = Get-WKSWorkspace | Where-Object {$_.ComputerName -eq "$computerName"} | Select-Object -Property WorkspaceId
  $global:workspaceId = $workspace_obj.WorkspaceId
}

function Get-RunList
{
  $runlist_obj = Get-WKSTag -ResourceId $workspaceId | Where-Object {$_.Key -eq 'RunList'} | Select-Object -Property Value
  $runlist_value = $runlist_obj.Value
  
  $global:cookbooks = $runlist_value.split(":")
}

function Download-Cookbooks
{
  Remove-Item -path ("$cookbooksPath" + "\*") -recurse
  Read-S3Object -BucketName $cookbookBucket -KeyPrefix "cookbooks" -Folder $cookbooksPath
}

function Strip-Versions
{
  ls $cookbooksPath | %{ ren ("$cookbooksPath" + "$_") $($_.name -replace "-\d+\..*")}
}

echo "Please wait while we install the required software..."
Install-Chef
Get-WorkspaceId
Get-RunList
Download-Cookbooks
Strip-Versions

# Reload PATH so we can find chef-client
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

$cookbooks.ForEach({
  # launch the chef client
  if ($nodeEnvironment)
  {
    chef-client -o $_ -E "$nodeEnvironment"
  }
  else
  {
    chef-client -o $_
  }
})
