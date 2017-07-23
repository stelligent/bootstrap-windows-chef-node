import boto3
import winrm, base64, subprocess, sys

client = boto3.client('ssm')

workspaces_username = "chef"
workspaces_ip = "34.195.157.83"
workspaces_password = client.get_parameter(Name='chef-winrm-password', WithDecryption=True)['Parameter']['Value']

command = """
Test-Path C:\chef
"""
session = winrm.Session(workspaces_ip, auth=(workspaces_username, workspaces_password))



r = session.run_ps(command)
print(r.std_out.decode(sys.stdout.encoding).replace('\r\n', '\n'))
