# Azure Work Item Reminder 

This program reminds team members of their active work items in Azure Devops

On Monday-Thursday, a report is sent to all individual team members with a list of all their active             work items

On Fridays a report is sent to the teams collective email, where all individials are listed along with          the items that they have set as active for more than 30 days

## Maintenance 

A Personal Access token is needed for this program to run. The token expires yearly. 

Link to obtain new access token:  [ Token](https://dev.azure.com/CBTS-Internal/_usersSettings/tokens)

## Changes 

If changes need to be made:
* Download EmailAlertsV2.zip 
* Open Visual Studio Code
* Download Azure Functions Extension if you have't already
* Log into Azure account on Visual Studio
* Makes changes to _init_.py
* Once you have completed the changes, select the WorkItemAlerts Function app on VS
* Deploy to function app








