from vsts.vss_connection import VssConnection
from msrest.authentication import BasicAuthentication
import vsts.work.v4_1.models as models
from vsts.work_item_tracking.v4_1.models.wiql import Wiql
from pprint import pprint
import itertools
import re
import smtplib
import os
from datetime import date




def choice(prompt, choices, representation):
    print(prompt)
    for id, choice in enumerate(choices):
        print("[{}] {}".format(id+1, representation(choice)))
    print("")

    choice = int(input(">> ")) - 1
    while choice < 0 or choice > len(choices):
        print("{} is not a valid choice".format(choice+1))
        choice = int(input(">> ")) - 1

    print("")
    return choice


# TODO I am not sure this function will be working whenever we reach some query limit. Although since there is a team context, it should only be limited by the ids within the team
# As far as I am aware the limit is 20k results. I am not sure if this will cause an exception or silently fail.
def get_max_id(work_tracking_client, team_context):
    wiql_query = Wiql(query='SELECT ID FROM workitems')
    query_results = work_tracking_client.query_by_wiql(wiql_query, team_context=team_context)

    return max([id.id for id in query_results.work_items])


def get_work_items_upto(work_tracking_client, team_context, max_id):
    MAX_AMOUNT = 200
    result = []
    # Azure DevOps limits the amount that can be retrieved to 200 at once
    for i in range(int(max_id / MAX_AMOUNT)):
        work_items = work_tracking_client.get_work_items(range(1+(MAX_AMOUNT * i), 1 + MAX_AMOUNT + (MAX_AMOUNT * i)))
        result.extend(work_items)
    return result




# Fill in with your personal access token and org URL
personal_access_token = 'token'
organization_url = 'org'

# Create a connection to the org
credentials = BasicAuthentication('', personal_access_token)
connection = VssConnection(base_url=organization_url, creds=credentials)

# Get a client (the "core" client provides access to projects, teams, etc)
core_client = connection.get_client('vsts.core.v4_0.core_client.CoreClient')

# Get the list of projects in the org
projects = core_client.get_projects()

# Project choice that the program will be looking inside and working with
##working_project = choice("Choose project:", projects, lambda project: project.name)
working_project = projects[0]


teams = core_client.get_teams(project_id=working_project.id)

#working_team = choice("Choose team:", teams, lambda team: team.name)
working_team = teams[0]


# Get work client for access to boards
work_client = connection.get_client('vsts.work.v4_1.work_client.WorkClient')
work_tracking_client = connection.get_client('vsts.work_item_tracking.v4_1.work_item_tracking_client.WorkItemTrackingClient')
team_context = models.TeamContext(project_id=working_project.id, team_id=working_team.id)
# Creates a query
wiql_query = Wiql(query="SELECT [Changed Date] FROM workitems WHERE [System.State] = 'Active' AND [Changed Date]<@Today-30")
# Obtains work item information
query_results = work_tracking_client.query_by_wiql(wiql_query, team_context=team_context)


# start a list to parse the work items data into
work_items = []

# loop through each work itme
for x in query_results.work_items:
    y=work_tracking_client.get_work_item(x.id)

    # break the azure devops data into simpler bits
    user = y.fields['System.AssignedTo']

    parts = user.split('<')

    name = parts[0].strip()

    email = parts[1].strip('>')

    priority = y.fields['Microsoft.VSTS.Common.Priority']

    idNum = str(y.id)

    url = "https://dev.azure.com/cbts-internal/Cloud-Transformation/_workitems/edit/" + idNum +"/"

    title = y.fields['System.Title']

    

    # setting data into the main dict
    tmp = {
        'Name': name,
        'Title': title,
        'Priority': priority,
        'Url': "https://dev.azure.com/cbts-internal/Cloud-Transformation/_workitems/edit/" + idNum +"/"
    }

    work_items.append(dict(tmp))
    
#pprint(work_items)

names = []
z=0
for entry in work_items:
    z=z+1
    
    if entry['Name'] not in names:
        names.append(entry['Name'])


#pprint(names)

for name in names:
    count = 0

    for item in work_items:
       
        if item['Name'] == name:
            count += 1
            result = "\n-----------------------------------------------------------------------------------------------------------------------------\n"+"Assigned to: "+ str(item['Name']) + "\nItem number: "+ str(count) + "\nTitle: " + str(item['Title']) + "\nPriority: " + str(item['Priority']) + "\nLink: " + str(item['Url'])
            print(result)    
            
            textFile=open("email.txt","a")
            textFile.write(result + "\n")
            
    textFile.write("-----------------------------------------------------------------------------------------------------------------------------\n\n")        
    personalCount = (str(name) + ": " + str(count) + " work-item(s)\n")
    countFile = open("count.txt","a")
    countFile.write(personalCount)
    
    textFile.close()
    countFile.close()     


    # if mon - thurs
    # send email to USER here
    # clear file you're writing to
    print("Day of the week: " + str(date.today().weekday()))
    print(str(count))
    if count > 0:
        if date.today().weekday() < 4:
            print("Mon-Thurs")
            def send_email(subject, msg):
                print(2)
                try:
                    print(3) 
                    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                    account = server.login("email", "pass")
                    message = 'Subject: {}\n\n{}'.format(subject, msg)
                    sendToUser = server.sendmail("email", email, message)    
                    server.quit()
                    print("Email sent successfully!!!!!!")
                except:
                    print("Email failed to send!")    
            subject = "Work-Item Alert"
            fileOut=open("email.txt", "r")
            fileContent = fileOut.read()
            countOut=open("count.txt", "r")
            countContent = countOut.read()
            if count == 1:
                msg = ("This active work-item has not been updated in the past 30 days.\n\n" + fileContent)
            if count >1:
                msg = ("These active work-items have not been updated in the past 30 days.\n\n" + fileContent)       
            fileOut.close()
            send_email(subject, msg)
        elif count == 0:
            print("no email")    
        os.remove("email.txt")
    
        

# if friday
# send email with all data
print("Day of the week: " + str(date.today().weekday()))
if z > 0:
    if date.today().weekday() == 4:
        print("Friday")
        def send_email(subject, msg):
            print(2)
            try:
                print(3) 
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                account = server.login("email", "pass")
                message = 'Subject: {}\n\n{}'.format(subject, msg)
                sendToTeam = server.sendmail("email", "team email", message)    
                server.quit()
                print("Email sent successfully!!!!!!")
            except:
                print("Email failed to send!")    
        subject = "Work-Item Alert"
        fileOut=open("email.txt", "r")
        fileContent = fileOut.read()
        countOut=open("count.txt", "r")
        countContent = countOut.read()
    
        if z == 1:
            msg = ("There is " + str(z) + " work-item that has not been updated in the past 30 days.\n\n" + fileContent)
        if z > 1:
            msg = ("These " + str(z) + " active work-items have not been updated in the past 30 days.\n\n"+countContent + fileContent)
        fileOut.close()
        countOut.close()
        send_email(subject, msg)
#Deletes file after sending the email so that next time the code runs it wont add to the past items
        os.remove("email.txt")
        os.remove("count.txt")  
elif z == 0:
    print("No email ")              
print(z)
exit()

