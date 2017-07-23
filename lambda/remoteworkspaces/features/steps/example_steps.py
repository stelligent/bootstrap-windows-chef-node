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

    workspaces_username = "chef"
    workspaces_ip = "34.195.157.83"
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

    workspaces_username = "chef"
    workspaces_ip = "34.195.157.83"
    workspaces_password = client.get_parameter(Name='chef-winrm-password', WithDecryption=True)['Parameter']['Value']

    command = """
    Test-Path D:\eclipse
    """
    session = winrm.Session(workspaces_ip, auth=(workspaces_username, workspaces_password))

    r = session.run_ps(command)

    formatted_response = str(r.std_out.decode('ascii').replace('\r\n', ""))

    formatted_response.should.be.equal("True")
