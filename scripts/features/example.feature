Feature: Showing off behave

  Scenario: Run a simple test
    Given we have behave installed
    When we winrm into the workspace and check if Chef is installed
    When we winrm into the workspace and check if Eclipse is installed
