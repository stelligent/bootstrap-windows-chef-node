import winrm
import boto3
import string
import json
from behave.__main__ import main as behave_main

def execute_tests():
  behave_main("features/example.feature")