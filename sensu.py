#!/usr/bin/env python

"""Interact with the Sensu API"""

import re
import json
import requests
import time
import logging
from datetime import datetime, timedelta

requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)


def process_response(response):
    if response.status_code in (200, 201, 202):
        return response.json()
    elif response.status_code == 204:
        return {}
    elif response.status_code == 401:
        raise Exception('Access denied')
    elif response.status_code == 404:
        raise Exception('Resource not found')
    else:
        print "response status code: %s" % response.status_code
        print "response body: %s" % response.json()
        raise Exception('Something went wrong, you should check the Sensu API')


def get_events(uri):
    response = requests.get(uri+'/events')
    result = process_response(response)
    return result


def get_stashes(uri, filter_path='silence'):
    response = requests.get(uri+'/stashes')
    all_stashes = process_response(response)
    filtered_stashes = []

    if filter_path:
        for stash in all_stashes:
            if re.search(r'^%s/.*' % (filter_path,), stash['path']):
                filtered_stashes.append(stash)

        return filtered_stashes
    else:
        return all_stashes


def get_stale_stashes(uri, stale_after, filter_path='silence'):
    stashes = get_stashes(uri, filter_path=filter_path)
    stale_stashes = []
    now = datetime.now()
    for stash in stashes:
        if 'expires' in stash['content']:
            expire_time = datetime.fromtimestamp(int(stash['content']['expires']))

            if now > expire_time:
                stale_stashes.append(stash)

        elif 'timestamp' in stash['content']:
            then = datetime.fromtimestamp(int(stash['content']['timestamp']))
            became_stale = then + timedelta(minutes=stale_after)

            if now > became_stale:
                stale_stashes.append(stash)

    return stale_stashes

def get_info(uri):
    response = requests.get(uri+'/info')
    result = process_response(response)
    return result

def delete_client(uri, client):
    response = requests.delete(uri+'/clients/'+client)
    result = process_response(response)
    return result

def resolve(uri, path):
    response = requests.delete(uri+'/events/'+path)
    result = process_response(response)
    return result

def silence(uri, owner, path, duration=None):
    genesis = datetime(1970,1,1)
    timestamp = int((datetime.now() - genesis).total_seconds())
    payload = {
        'path': 'silence/'+path,
        'content': {
            'owner': owner,
            'timestamp': timestamp
        }
    }

    if duration is None:
        pass
    else:
        payload['expire'] = int(duration) * 60

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    response = requests.post(uri+'/stashes', data=json.dumps(payload), headers=headers)

    result = process_response(response)
    return result


def unsilence(uri, path):
    response = requests.delete(uri+'/stashes/silence/'+path)
    result = process_response(response)
    return result
