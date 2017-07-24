import boto3
import winrm, base64, subprocess, sys
import sure
from behave import *

@when(u'the workspace has been provisioned')
def step_impl(context):
    context.workspace_ip = find_public_ip_of_workspace()

@then('Chef is installed')
def step_impl(context):
    session = create_session(context.workspace_ip)

    command = """
    Test-Path C:\opscode\chef
    """
    r = session.run_ps(command)

    actual_response = str(r.std_out.decode('ascii').replace('\r\n', ""))
    expected_response = "True"

    actual_response.should.be.equal(expected_response)
    print(actual_response)

@then('Eclispe is installed')
def step_impl(context):
    session = create_session(context.workspace_ip)

    command = """
    Test-Path D:\eclipse\eclipse.exe
    """
    r = session.run_ps(command)

    actual_response = str(r.std_out.decode('ascii').replace('\r\n', ""))
    expected_response = "True"

    actual_response.should.be.equal(expected_response)

def create_session(workspaces_ip):
    client = boto3.client('ssm')

    workspaces_username = "chef"
    workspaces_password = client.get_parameter(Name='chef-winrm-password', WithDecryption=True)['Parameter']['Value']
    session = winrm.Session(workspaces_ip, auth=(workspaces_username, workspaces_password))
    return session

def find_public_ip_of_workspace():
    ec2 = boto3.client('ec2')
    workspaces = boto3.client('workspaces')
    cloudformation = boto3.resource('cloudformation')

    stack = cloudformation.Stack('WorkspaceBuilder')
    stack_resource = stack.Resource('workspace1').physical_resource_id
    workspace_private_ip = workspaces.describe_workspaces(WorkspaceIds=[stack_resource])['Workspaces'][0]['IpAddress']
    workspace_public_ip = ec2.describe_network_interfaces(Filters=[{ 'Name' : 'private-ip-address', 'Values' : [workspace_private_ip] }])['NetworkInterfaces'][0]['Association']['PublicIp']
    return workspace_public_ip