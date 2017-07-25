import winrm
import boto3
import string
import json

ssm = boto3.client('ssm')
ec2 = boto3.client('ec2')
workspaces = boto3.client('workspaces')
cloudformation = boto3.resource('cloudformation')

def find_public_ip_of_workspace():
    stack = cloudformation.Stack('WorkspaceBuilder')
    stack_resource = stack.Resource('workspace1').physical_resource_id
    workspace_private_ip = workspaces.describe_workspaces(WorkspaceIds=[stack_resource])['Workspaces'][0]['IpAddress']
    workspace_public_ip = ec2.describe_network_interfaces(Filters=[{ 'Name' : 'private-ip-address', 'Values' : [workspace_private_ip] }])['NetworkInterfaces'][0]['Association']['PublicIp']
    return workspace_public_ip

def find_id_of_workspace():
    stack = cloudformation.Stack('WorkspaceBuilder')
    stack_resource = stack.Resource('workspace1').physical_resource_id
    return stack_resource

def update_workspace_running_mode():
    workspace_id = find_id_of_workspace()
    workspaces.modify_workspace_properties(
        WorkspaceId=workspace_id,
        WorkspaceProperties={
            'RunningMode': 'AUTO_STOP',
            'RunningModeAutoStopTimeoutInMinutes': 60
        }
    )

def install_chef():
    workspaces_username = "chef"
    workspaces_ip = find_public_ip_of_workspace()
    workspaces_password = ssm.get_parameter(Name='chef-winrm-password', WithDecryption=True)['Parameter']['Value']
    access_key = ssm.get_parameter(Name='snhu-workspace-user-access-key', WithDecryption=True)['Parameter']['Value']
    secret_access_key = ssm.get_parameter(Name='snhu-workspace-user-secret-key', WithDecryption=True)['Parameter']['Value']

    command ="""
    Set-ExecutionPolicy RemoteSigned -force
    Import-Module "C:\Program Files (x86)\AWS Tools\PowerShell\AWSPowerShell\AWSPowerShell.psd1"
    Set-AWSCredential -AccessKey %(access_key)s -SecretKey %(secret_access_key)s -StoreAs default
    . { iwr -useb https://omnitruck.chef.io/install.ps1 } | iex; install -channel stable -project chef
    """ % locals()

    s = winrm.Session(workspaces_ip, auth=(workspaces_username, workspaces_password))

    response = s.run_ps(command)
    print(response.std_err)
    print(response.std_out.decode('ascii').replace('\r\n', "\n"))

install_chef()
