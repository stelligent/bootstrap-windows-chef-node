import boto3
import winrm, base64, subprocess, sys
import sure
from behave import *

@given('we have behave installed')
def step_impl(context):
    pass

@when('we winrm into the workspace and check if Chef is installed')
def step_impl(context):
    client = boto3.client('ssm')

    workspaces_username = "Chef"
    workspaces_ip = find_public_ip_of_workspace()
    workspaces_password = client.get_parameter(Name='chef-winrm-password', WithDecryption=True)['Parameter']['Value']

    command = """
    Test-Path C:\chef
    """
    session = winrm.Session(workspaces_ip, auth=(workspaces_username, workspaces_password))

    r = session.run_ps(command)

    formatted_response = str(r.std_out.decode('ascii').replace('\r\n', ""))

    formatted_response.should.be.equal("True")

@when('we winrm into the workspace and check if Eclipse is installed')
def step_impl(context):
    client = boto3.client('ssm')

    workspaces_username = "Chef"
    workspaces_ip = find_public_ip_of_workspace()
    workspaces_password = client.get_parameter(Name='chef-winrm-password', WithDecryption=True)['Parameter']['Value']

    command = """
    Test-Path D:\eclipse
    """
    session = winrm.Session(workspaces_ip, auth=(workspaces_username, workspaces_password))

    r = session.run_ps(command)

    formatted_response = str(r.std_out.decode('ascii').replace('\r\n', ""))

    formatted_response.should.be.equal("True")

def find_public_ip_of_workspace():
    cloudformation = boto3.resource('cloudformation')
    ec2 = boto3.client('ec2')
    workspaces = boto3.client('workspaces')

    stack = cloudformation.Stack('WorkspaceBuilder')
    stack_resource = stack.Resource('workspace1').physical_resource_id
    workspace_private_ip = workspaces.describe_workspaces(WorkspaceIds=[stack_resource])['Workspaces'][0]['IpAddress']
    workspace_public_ip = ec2.describe_network_interfaces(Filters=[{ 'Name' : 'private-ip-address', 'Values' : [workspace_private_ip] }])['NetworkInterfaces'][0]['Association']['PublicIp']
    return workspace_public_ip
