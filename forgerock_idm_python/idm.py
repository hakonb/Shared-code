import os
import re
import json
import requests
import pprint 

pp = pprint.PrettyPrinter(indent=4)

env = {
	'local' : {
		'endpoint' : 'http://localhost:8080/', 
		'username' : 'openidm-admin', 
		'password' : 'openidm-admin'},
	'test' : {
		'endpoint' : 'http://testidm.example.com:8080/', 
		'username' : 'openidm-admin', 
		'password' : os.environ['IDM_TEST_PASSWORD']
	},
	'prod' : {
		'endpoint' : 'http://idm.example.com:8080/', 
		'username' : os.environ['IDM_PROD_USERNAME'], 
		'password' : os.environ['IDM_PROD_PASSWORD']
	}
}

def headers(environment): 
	return {
    	'X-OpenIDM-Username': env[environment]['username'],
    	'X-OpenIDM-Password': env[environment]['password'],
    	'accept': 'application/json',
    	'Accept-API-Version': 'resource=1.0',
    	'Content-Type': 'application/json',
	}

def get(environment, path):
	url = env[environment]['endpoint'] + path
	response = requests.get(url, headers=headers(environment))
	
	if response.status_code == 200:
		return response.json()
	else:	
		print( 'ERROR: ' + str(response.status_code) + ' - ' + str(response.reason) + ' for ' + url)
	return []
  
def post(environment, url, data=[]):
	response = requests.post(url, headers=headers(environment), params=() ,data=data)
	if response.status_code == 200:
		print( 'OK' )
	else:
		print( 'ERROR (patch): ' + str(response.status_code) + ' - ' + str(response.reason) + ' for ' + url )
    
def getManagedLink(environment, model, id):
    return env[environment]['endpoint'] + 'admin/#resource/managed/'+model+'/edit/' + id

def getManaged(environment, model, filter='true', fields=''):
	url = env[environment]['endpoint'] + 'openidm/managed/' + model
	if fields:
		params = ( ('_queryFilter', filter), ('_fields', fields))
	else:
		params = ( ('_queryFilter', filter), ) 
	response = requests.get(url, headers=headers(environment), params=params)
	
	if response.status_code == 200:
		return response.json()['result']
	else:	
		print( 'ERROR: ' + str(response.status_code) + ' - ' + str(response.reason) + ' (' + model+ ')')
	return []

def patchManaged(environment='local', model='user', id='', data=[]):
	url = env[environment]['endpoint'] + 'openidm/managed/' + model + '/' + id
	response = requests.patch(url, headers=headers(environment), params=() ,data=data)
	if response.status_code == 200:
		print( 'OK' )
	else:
		print( 'ERROR (patch): ' + str(response.status_code) + ' - ' + str(response.reason) + ' for ' + url )
			
def getLookup(environment, model, filter='true', key='_id', field=''):
    objects = getManaged(environment, model, filter)
    lookup = {}
    for object in objects:
        if key in object:
            if field:
                lookup[ object[key] ] = object.get(field, None)
            else:
                lookup[ object[key] ] = object
    return lookup

def send_mail(environment, to, subject='Test mail', body='<h1>This is a test</h1>', type='text/html' ):
    url = env[environment]['endpoint'] + 'openidm/external/email?_action=send'
    data = json.dumps( {"to": to, "from": 'noreply@example.com', "subject": subject, "body": str(body), "type": type} )
    response = requests.post( url, headers=headers(environment), data=data )

    if response.status_code == 200:
        print( 'OK' )
    else:
        print( 'ERROR: ' + str(response.status_code) + ' - ' + str(response.reason) ) 
    
def addRoleMember(environment, user_id, role_id, message):
	print(message, end=': ')
	url = env[environment]['endpoint'] + 'openidm/managed/role/' +role_id+ '/members'
	data = '{ "_ref": "managed/user/'+user_id+'", "_refProperties": { "_id": "'+user_id+'" }}'
	response = requests.post(url, headers=headers(environment), data=data)	
		
	if response.status_code == 201:
		print( 'OK' )
	elif response.status_code == 412:
		print( 'WARNING: Precondition Failed. Already a member?' )
	else:
		print( 'ERROR: ' + str(response.status_code) + ' - ' + str(response.reason) )
        
def runUserRecon(environment, userName, mapping):
    user = getManaged(environment, 'user', 'userName eq "'+userName+'"', '_id')
    #print(user)
    if user:
        url = env[environment]['endpoint'] + 'openidm/recon?mapping=' + mapping + '&id=' + user[0]['_id'] + '&_action=reconById'
        print(url)
        post(environment, url)
    

