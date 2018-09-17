import winrm
import boto3
import string
import json

ssm = boto3.client('ssm')
ec2 = boto3.client('ec2')
workspaces = boto3.client('workspaces')
cloudformation = boto3.resource('cloudformation')

def execute_chef():
    workspaces_username = "Chef"
    workspaces_ip = find_public_ip_of_workspace()
    workspaces_password = ssm.get_parameter(Name='chef-winrm-password', WithDecryption=True)['Parameter']['Value']
    access_key = ssm.get_parameter(Name='workspace-user-access-key', WithDecryption=True)['Parameter']['Value']
    secret_access_key = ssm.get_parameter(Name='workspace-user-secret-key', WithDecryption=True)['Parameter']['Value']
    chef_path = "C:\chef"
    cookbooks_path = "C:\chef\cookbooks"
    cookbooks_bucket = "workspaces-cookbooks-us-west-2"

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
    print(response.std_out.decode('ascii').replace('\r\n', "\n"))

def find_public_ip_of_workspace():
    stack = cloudformation.Stack('WorkspaceBuilder')
    stack_resource = stack.Resource('workspace1').physical_resource_id
    workspace_private_ip = workspaces.describe_workspaces(WorkspaceIds=[stack_resource])['Workspaces'][0]['IpAddress']
    workspace_public_ip = ec2.describe_network_interfaces(Filters=[{ 'Name' : 'private-ip-address', 'Values' : [workspace_private_ip] }])['NetworkInterfaces'][0]['Association']['PublicIp']
    return workspace_public_ip

execute_chef()
