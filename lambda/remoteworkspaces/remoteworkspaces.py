import winrm
import boto3
import string
import json

code_pipeline = boto3.client('codepipeline')
client = boto3.client('ssm')
s3 = boto3.client('s3')
ec2 = boto3.client('ec2')
workspaces = boto3.client('workspaces')

def get_workspace_public_ip(event, context):
  if event['CodePipeline.job']:
    input_artifact = event['CodePipeline.job']['data']['inputArtifacts']
    s3_bucket = input_artifact['location']['s3location']['bucketName']
    s3_key = input_artifact['location']['s3location']['objectKey']

    output_json_string = s3.get_object(
      Bucket=s3_bucket,
      Key=s3_key
    )

    print(output_json_string['Body'].read())

def install_chef(event, context):
    if event['CodePipeline.job']:
      job_id = event['CodePipeline.job']['id']
    else:
      job_id = None
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

    continue_job_later(job_id, 'Chef install started...')

    response = s.run_ps(command)
    print(response.std_err)
    print(response.std_out)

    if job_id:
      if response.status_code == 0:
        put_job_success(job_id, "Chef successfully installed")
      else:
        put_job_failure(job_id, "Chef installation failed")

def execute_chef(event, context):
    if event['CodePipeline.job']:
      job_id = event['CodePipeline.job']['id']
    else:
      job_id = None
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

    continue_job_later(job_id, 'Chef execution started...')

    response = session.run_ps(command)
    
    print(response.std_err)
    print(response.std_out)

    if job_id:
      if response.status_code == 0:
        put_job_success(job_id, "Chef successfully executed")
      else:
        put_job_failure(job_id, "Chef execution failed")

def put_job_success(job, message):
    """Notify CodePipeline of a successful job
    
    Args:
        job: The CodePipeline job ID
        message: A message to be logged relating to the job status
        
    Raises:
        Exception: Any exception thrown by .put_job_success_result()
    
    """
    print('Putting job success')
    print(message)
    code_pipeline.put_job_success_result(jobId=job)
  
def put_job_failure(job, message):
    """Notify CodePipeline of a failed job
    
    Args:
        job: The CodePipeline job ID
        message: A message to be logged relating to the job status
        
    Raises:
        Exception: Any exception thrown by .put_job_failure_result()
    
    """
    print('Putting job failure')
    print(message)
    code_pipeline.put_job_failure_result(jobId=job, failureDetails={'message': message, 'type': 'JobFailed'})
 
def continue_job_later(job, message):
    """Notify CodePipeline of a continuing job
    
    This will cause CodePipeline to invoke the function again with the
    supplied continuation token.
    
    Args:
        job: The JobID
        message: A message to be logged relating to the job status
        continuation_token: The continuation token
        
    Raises:
        Exception: Any exception thrown by .put_job_success_result()
    
    """
    
    # Use the continuation token to keep track of any job execution state
    # This data will be available when a new job is scheduled to continue the current execution
    continuation_token = json.dumps({'previous_job_id': job})
    
    print('Putting job continuation')
    print(message)
    code_pipeline.put_job_success_result(jobId=job, continuationToken=continuation_token)
