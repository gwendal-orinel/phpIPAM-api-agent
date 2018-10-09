#!/usr/bin/python

import urllib,urllib2
import json
import time
import base64
import ipaddress
import subprocess
from datetime import datetime

IP = "IP"
agent_name = "AGENT_NAME"

app = "APP"
username = "USER"
password = "PASS"

headers = { 'Content-Type': 'application/json','Accept':'application/json' }
login = base64.b64encode('%s:%s' % (username, password))

def now():
  return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def get_token():
  global token
  url = 'http://'+IP+'/api/'+app+'/user/'
  req = urllib2.Request(url,'', headers)
  req.add_header("Authorization", "Basic %s" % login)
  try:
    response = urllib2.urlopen(req, timeout = 30).read()
    token = json.loads(response)['data']['token']
    return token
  except urllib2.HTTPError, err:
    message =  err.read()
    message_content =  json.loads(message)['message']
    print "Error: "+message_content
    exit()
  except urllib2.URLError, e:
    print "Error: "+str(e.reason)+" ("+IP+")"
    exit()


def get_scan_agent():
  global scan_agent
  url = 'http://'+IP+'/api/'+app+'/tools/scanagents/'
  req = urllib2.Request(url)
  req.add_header('token',token)
  response = urllib2.urlopen(req).read()
  agent_list = json.loads(response)['data']
  for agent in agent_list:
    if agent['name'] == agent_name:
      scan_agent = agent['id']
  if not scan_agent:
    print "No matching scan-agent found"
    exit()

def get_sections_list():
  global sections_list
  sections_list = []
  url = 'http://'+IP+'/api/'+app+'/sections/'
  req = urllib2.Request(url)
  req.add_header('token',token)
  response = urllib2.urlopen(req).read()
  list = json.loads(response)['data']
  for section in list:
    id = str(section['id'])
    sections_list.append(id)
  if not sections_list:
    print "No sections found"
    exit()

def get_subnet_list():
  global subnet_list
  subnet_list = []
  for sectionID in sections_list:
    url = 'http://'+IP+'/api/'+app+'/sections/'+sectionID+'/subnets/'
    req = urllib2.Request(url)
    req.add_header('token',token)
    response = urllib2.urlopen(req).read()
    list = json.loads(response)['data']
    for subnet in list:
      id = str(subnet['id'])
      net = str(subnet['subnet']+'/'+subnet['mask'])
      agent = str(subnet['scanAgent'])
      if agent ==  scan_agent: #si il a le scan_agent cible
        subnet_list.append(id+','+net)
  if not subnet_list:
    print "No matching subnets found"
    exit()
  print "Subnets :"+str(subnet_list)

def get_address_by_id(ip,subnetid,tag):
   url = 'http://'+IP+'/api/'+app+'/addresses/'+ip+'/'+subnetid+'/'
   req = urllib2.Request(url)
   req.add_header('token',token)
   response = urllib2.urlopen(req).read()
   exist = json.loads(response)['success']
   if exist == 1:
     status =  json.loads(response)['data']['state']
     if str(status) == str(tag):
       return -1
     else:
       addressID = json.loads(response)['data']['id']
       return addressID
   else:
     return 0

def update_existing_ip(tag,addressID):
  template='{ "tag": '+str(tag)+',"note":"Last update: '+now()+'" }'
  url = 'http://'+IP+'/api/'+app+'/addresses/'+addressID+'/'
  req = urllib2.Request(url, template, headers)
  req.get_method = lambda: 'PATCH'
  req.add_header('token',token)
  response = urllib2.urlopen(req).read()
  status = json.loads(response)['message']
  print status

def create_ip(subnetid,ip,tag):
  template='{ "ip": "'+ip+'", "subnetId": '+str(subnetid)+', "tag": '+str(tag)+',"note":"Last update: '+now()+'" }'
  url = 'http://'+IP+'/api/'+app+'/addresses/'
  req = urllib2.Request(url, template, headers)
  req.add_header('token',token)
  response = urllib2.urlopen(req).read()
  status = json.loads(response)['message']
  print status

def check_host():
  for network in subnet_list:
    id,subnet = network.split(',')
    ip_net = ipaddress.ip_network(unicode(subnet))
    all_hosts = list(ip_net.hosts())
    for ip in all_hosts:
      cmd = "/bin/ping -c 3 -i 0.5 -s 24 "+ str(ip)
      response = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT).communicate()[0]
      if 'bytes from' in response :
        print str(ip)+": Online"
        tag=2
        addressID = get_address_by_id(str(ip),str(id),tag)
        if addressID == 0:
          create_ip(str(id),str(ip),tag)
        elif addressID == -1:
          print "No update needed"
        else:
          update_existing_ip(tag,addressID)
      else:
        print str(ip)+": Offline"
        tag=1
        addressID = get_address_by_id(str(ip),str(id),tag)
        if addressID == 0:
          print "Not used"
        elif addressID == -1:
          print "No update needed"
        else:
          update_existing_ip(tag,addressID)



print "Scan started at: "+now()
get_token()
get_scan_agent()
get_sections_list()
get_subnet_list()
check_host()

print "Scan Finished at: "+now()
