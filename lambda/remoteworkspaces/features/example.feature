Feature: Workspaces are provisioned

  As a devops engineer
  I would like to verify that a Workspace is provisioned correctly with an automated test
  So that verifications are reproducible and not ad-hoc

# we'd verify versions too in a more realistic scenario
Scenario: Smoke Test for Eclipse
  When the workspace has been provisioned
  Then Chef is installed
   And Eclispe is installed