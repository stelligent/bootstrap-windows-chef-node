import winrm
import boto3
import string

def install_chef(event, context):
    client = boto3.client('ssm')

    workspaces_username = "chef"
    workspaces_ip = "34.230.188.79"
    workspaces_password = client.get_parameter(Name='chef-winrm-password', WithDecryption=True)['Parameter']['Value']
    access_key = client.get_parameter(Name='snhu-workspace-user-access-key', WithDecryption=True)['Parameter']['Value']
    secret_access_key = client.get_parameter(Name='snhu-workspace-user-secret-key', WithDecryption=True)['Parameter']['Value']

    command ="""
    Set-ExecutionPolicy RemoteSigned -force
    Import-Module "C:\Program Files (x86)\AWS Tools\PowerShell\AWSPowerShell\AWSPowerShell.psd1"
    Set-AWSCredential -AccessKey %(access_key)s -SecretKey %(secret_access_key)s -StoreAs default
    . { iwr -useb https://omnitruck.chef.io/install.ps1 } | iex; install -channel stable -project chef
    """ % locals()

    s = winrm.Session(workspaces_ip, auth=(workspaces_username, workspaces_password))

    r = s.run_ps(command)
    print(r.std_err)
    print(r.std_out)

def execute_chef(event, context):
    client = boto3.client('ssm')

    workspaces_username = "chef"
    workspaces_ip = "34.230.188.79"
    workspaces_password = client.get_parameter(Name='chef-winrm-password', WithDecryption=True)['Parameter']['Value']
    access_key = client.get_parameter(Name='snhu-workspace-user-access-key', WithDecryption=True)['Parameter']['Value']
    secret_access_key = client.get_parameter(Name='snhu-workspace-user-secret-key', WithDecryption=True)['Parameter']['Value']
    chef_path = "C:\chef"
    cookbooks_path = "C:\chef\cookbooks"
    cookbooks_bucket = "snhu-chef"

    command ="""
    Set-ExecutionPolicy RemoteSigned -force
    Import-Module "C:\Program Files (x86)\AWS Tools\PowerShell\AWSPowerShell\AWSPowerShell.psd1"
    Set-AWSCredential -AccessKey %(access_key)s -SecretKey %(secret_access_key)s -StoreAs default
    if(!(Test-Path "%(chef_path)s")) {
      New-Item "%(chef_path)s" -ItemType Directory -Force
    }
    if(!(Test-Path "%(cookbooks_path)s")) {
      New-Item "%(cookbooks_path)s" -ItemType Directory -Force
    }
    Remove-Item -path ("%(cookbooks_path)s" + "\*") -recurse
    Read-S3Object -BucketName "%(cookbooks_bucket)s" -KeyPrefix "cookbooks" -Folder "%(cookbooks_path)s"
    chef-solo -o snhu-eclipse
    """ % locals()

    session = winrm.Session(workspaces_ip, auth=(workspaces_username, workspaces_password))

    response = session.run_ps(command)

    print(response.std_err)
    print(response.std_out)
