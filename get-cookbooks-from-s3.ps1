# Credits: Based on the bash version in the AWS OpsWorks docs: http://docs.aws.amazon.com/opsworks/latest/userguide/opscm-unattend-assoc.html
# Settings: Change chefServerName and chefServerEndpoint at a minimum

# Required settings
$global:region              = "us-east-1"
$global:computerName	    = $env:ComputerName
$global:chefPath	    = "C:\chef"
$global:cookbookBucket	    = "snhu-cookbooks"

# Recommended: upload the chef-client cookbook from the chef supermarket  https://supermarket.chef.io/cookbooks/chef-client
# Use this to apply sensible default settings for your chef-client configuration like logrotate, and running as a service.
# You can add more cookbooks in the run list, based on your needs

function Get-InstanceId
{
    Invoke-RestMethod -Uri http://169.254.169.254/latest/meta-data/instance-id
}

function Install-Chef
{
  . { iwr -useb https://omnitruck.chef.io/install.ps1 } | iex; install -channel $chefClientVersion -project chef
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
    $cookbooks.ForEach({
        if(!(Test-Path $chefPath + "\cookbooks\" + $_))
        {
            New-Item $chefPath + "\cookbooks\" + $_ -type directory
        }

        Read-S3Object -BucketName $cookbookBucket -KeyPrefix $_ -Folder $chefPath + "\cookbooks\" + $_
    })
}


Install-Chef
$instanceId = Get-InstanceId
Get-WorkspaceId
Get-RunList
Download-Cookbooks

# Reload PATH so we can find chef-client
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# launch the chef client
if ($nodeEnvironment)
{
  chef-client -r "$runList" -E "$nodeEnvironment"
}
else
{
    chef-client -r "$runList"
}