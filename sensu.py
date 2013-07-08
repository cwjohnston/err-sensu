#!/usr/bin/env python

"""Interact with the Sensu API"""

import re
import json
import requests
import time
from datetime import datetime, timedelta


def process_response(response):
    if response.status_code in (200, 201,):
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


def get_silenced(uri):
    silenced = []
    stashes = get_stashes(uri)
    for stash in stashes:
        if re.search(r'^silence/.*', stash['path']):
            silenced.append(stash)
    return silenced


def get_stashes(uri):
    response = requests.get(uri+'/stashes')
    result = process_response(response)
    return result


def resolve(uri, path):
    pass


def silence(uri, owner, path, duration=None):
    dt = datetime.now()
    timestamp = time.mktime(dt.timetuple())
    payload = {'owner': owner, 'timestamp': timestamp}

    if duration is None:
        pass
    else:
        dt = datetime.now()
        expire_time = dt + timedelta(minutes=duration)
        expire_timestamp = time.mktime(expire_time.timetuple())
        payload['expires'] = expire_timestamp

    response = requests.post(uri+'/stashes/silence/'+path, data=json.dumps(payload))

    result = process_response(response)
    return "Created a silence stash at %s/stashes/%s" % (uri, result['path'],)


def unsilence(uri, path):
    response = requests.delete(uri+'/stashes/silence/'+path)
    result = process_response(response)
    return "Deleted stash at %s/stashes/silence/%s" % (uri, path,)
