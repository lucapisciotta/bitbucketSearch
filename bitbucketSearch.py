from ast import literal_eval
from shutil import which
from sys import platform
import json
import logging
import os
import requests
import subprocess

attempt = 0
if os.path.dirname(__file__) != '':
    basePath = os.path.dirname(__file__)
else:
    basePath = os.getcwd()
baseUrl = 'https://api.bitbucket.org/2.0'
bitbucket_workspace = 'musemencom'
credential_file = "%s%s" % (basePath, '/credentials.json')
pagelen = 100  # 100 is the limit for repository API request
repository_folder = "%s%s" % (basePath, '/buckets/')
repository_response_path = "%s%s" % (basePath, '/repository_response.json')
if platform == 'darwin':
    logging.info('You\'re running this script in OS X')
    required_software = ['trufflehog3', 'git-credential-osxkeychain']
else:
    logging.warning('I haven\'t tested the script in this OS yet, you need a git credential helper software installed')
    required_software = ['trufflehog3']
tokenUrl = 'https://bitbucket.org/site/oauth2/access_token'
tokenValue = ''
trufflehog_format = 'yaml'  # Valid format are {json, yaml and html}
trufflehog_rules_path = "%s%s" % (basePath, '/secrets.yaml')
userKey = ''
userSecret = ''

s = requests.Session()
logging.basicConfig(level=logging.INFO)


def check_requirements():
    for software in required_software:
        try:
            if which(software) is not None:
                logging.info('[√] - ' + software + ' instaled')
            else:
                raise Exception
        except Exception:
            logging.error('[X] - ' + software + ' not instaled')
            exit()


def load_credential():
    logging.info("Loading credentials...")
    global userKey, userSecret
    with open(credential_file, 'r') as cred_file:
        credentials = cred_file.read()
        credentials = json.loads(credentials)
        userKey = credentials['userKey']
        userSecret = credentials['userSecret']
    check_if_token_exist()


def load_token():
    logging.info("Loading token...")
    global tokenValue
    if os.path.getsize(basePath + '/token.json') > 0:
        with open(basePath + '/token.json', 'r') as json_file:
            tokenValue = json_file.read()
            tokenValue = json.loads(tokenValue)
    else:
        retrieve_token()


def retrieve_token():
    data = {'grant_type': 'client_credentials'}
    response = s.post(tokenUrl, data=data, auth=(userKey, userSecret))
    response_content = literal_eval(response.content.decode('utf8'))
    with open(basePath + '/token.json', 'w') as token_file:
        token_file.truncate()
        json.dump(response_content, token_file, indent=3, sort_keys=True)
    logging.info("A new token is available")


def check_if_token_exist():
    logging.info("Check if token exists...")
    if os.path.exists(basePath + '/token.json') and os.path.getsize(basePath + '/token.json') > 0:
        check_if_token_is_valid()
    else:
        logging.warning("Token does not exist, retrieving a token...")
        retrieve_token()


def check_if_token_is_valid():
    load_token()
    request_header = {'Authorization': '{} {}'.format(str(tokenValue['token_type']).capitalize(), str(tokenValue['access_token']))}
    response = s.get(baseUrl + '/user', headers=request_header)
    if response.status_code in [401, 403]:
        logging.warning('You\'re not authorized anymore')
        refresh_token(str(tokenValue['refresh_token']))


def refresh_token(refresh_token_value):
    global attempt
    if attempt == 0:
        logging.info("I am trying to refresh your old token...")
        data = {'grant_type': 'refresh_token', 'refresh_token': refresh_token_value}
        response = s.post(tokenUrl, data=data, auth=(userKey, userSecret))
        response_content = response.content
        response_json = json.loads(response_content)
        auth_token = response_json['access_token']
        with open(basePath + '/token.json', 'r+') as json_file:
            data = json.load(json_file)
            data['access_token'] = auth_token
            json_file.seek(0)
            json.dump(data, json_file, indent=3)
            attempt = 1
        check_if_token_is_valid()
    elif attempt == 1:
        logging.warning('Your token is not valid, retrieving a new token')
        attempt = 0
        retrieve_token()


def retrieve_repositories_list():
    repository_list_name = []
    check_if_token_exist()
    logging.info("Retrieving repositories list...\n")
    try:
        last_page = False
        while not last_page:
            request_header = {'Authorization': '{} {}'.format(str(tokenValue['token_type']).capitalize(), str(tokenValue['access_token']))}
            params = (('pagelen', pagelen), ('page', 1),)
            if 'next_page' in locals():
                repository_list = s.get(next_page, headers=request_header)
            else:
                repository_list = s.get(baseUrl + '/repositories/' + bitbucket_workspace, headers=request_header, params=params)
            repository_list_content = json.loads(repository_list.content)
            for repository_name in repository_list_content['values']:
                repository_list_name.append(repository_name['full_name'])
            try:
                next_page = repository_list_content['next']
            except:
                last_page = True
    except Exception as e:
        logging.error(e)
    return repository_list_name


def run_trufflehog(repository_name=None):
    clean_repository_name = repository_name.partition('/')[2]
    logging.info('I\'m looking for something special in ' + repository_name)
    try:
        command = 'trufflehog3 -f ' + trufflehog_format + ' --no-entropy -r ' + trufflehog_rules_path + ' https://bitbucket.org/' + repository_name
        command_response = subprocess.getoutput(command)
        if command_response != '':
            with open(repository_folder + clean_repository_name + '.' + trufflehog_format, 'w') as repository_report:
                repository_report.truncate()
                repository_report.write(command_response)
    except Exception as e:
        logging.error(e)
        raise


check_requirements()
load_credential()
for repository in retrieve_repositories_list():
    run_trufflehog(repository)
