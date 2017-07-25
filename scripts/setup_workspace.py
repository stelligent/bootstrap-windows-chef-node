import boto3
import string
import json

workspaces = boto3.client('workspaces')
cloudformation = boto3.resource('cloudformation')

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