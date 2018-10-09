# phpIPAM-api-agent
An python api agent developped for phpIPAM solution

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
