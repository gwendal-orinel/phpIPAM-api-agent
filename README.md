# phpIPAM-api-agent
An python api agent developped for phpIPAM solution      
*Created by Gwendal Orinel*

[phpIPAM](https://github.com/phpipam/phpipam)


# How to deploy ?

## Declare Agent on main server 
### By API:
Get api token with:
```
curl -X POST --user USERNAME:PASSWORD https://URL/api/operator/user/
```
Copy token in header & set NAME and DESCRIPTION:
```
curl -X POST -H 'token: TOKEN' -H 'Content-Type: application/json' -d '{ "name":"NAME","type":"api","description":"DESCRIPTION" }' https://URL/api/operator/tools/scanagents/ 
```
### By GUI: 
Go at: https://URL/administration/scan-agents/  
It’s preferable to create it via API because GUI doesn’t propose API agent type, it’s not necessary but it’s more understandable.        Code field is not used too, so it can be a random value.

## Install
### Download python script:
  - phpipam_agent_api.py

### Install
  - Put it in /var/phpipam_agent_api.py
  - chmod +x /var/phpipam_agent_api.py

### Configure Agent
In python script change variable for matching to main server:
  - IP : ip of main server
  - agent_name: Name of agent previously created
  - app: app name of api key (“operator” in our case)
  - username: phpipam username
  - password: phpipam password
  
### Schedule the agent
Create crontab every hour:
```
0 */1 * * * python /var/phpipam_agent_api.py > /var/log/phpipam_agent_api.log
```

# How to Use ?
- On phpIPAM main server, for each outside networks accessible from agents server and declared in phpIPAM, edit subnet and activate check hosts status and select your agent
- Every hour, agent will check and update subnet.
- In bottom subnet available table, 3 colors are used:
  - Green color: IP is used
  - White color: IP is not used
  - Red color: IP was used but offline now, it may be able to be release?
  
# How to Supervise ?
The log file is available in /var/log/phpipam_agent_api.log
- Subnets on first line correspond to all subnets found by the agent that have a matched scanagent params activated.
- For each IP scanned you can see its status, and below, the api action performed.
> If you have some troubles check this file or cron log at /var/log/cron
