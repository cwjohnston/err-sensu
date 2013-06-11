from errbot import BotPlugin, botcmd

import config
import logging
import requests
from collections import Counter

from sensu import get_events, get_stashes, get_silenced, silence, unsilence


class Sensu(BotPlugin):
    """An Err plugin Sensu"""
    min_err_version = '1.6.0' # Optional, but recommended
    max_err_version = '2.0.0' # Optional, but recommended

    def get_configuration_template(self):
        """Defines the configuration structure this plugin supports"""
        return {'ENDPOINTS':[{'ENVIRONMENT': 'staging', 'URI': 'http://sensu.staging.example.com'}]}

    def resolve_endpoint(self, env):
        """ Returns API endpoint URI """
        uri = None
        for endpoint in self.config['ENDPOINTS']:
            if endpoint['ENVIRONMENT'] == env:
                uri = endpoint['URI']
            else:
                pass

        if uri is None:
            raise Exception('Sorry, I could not match your request to a known API endpoint')
        else:
            return uri

    def summarize_events(self, uri):
        events = get_events(uri)
        event_counter = Counter()

        for event in events:
            if event['flapping'] == True:
                event_counter['flapping'] += 1
            if event['status'] == 2:
                event_counter['critical'] += 1
            elif event['status'] == 1:
                event_counter['warning'] += 1
            elif event['status'] == 0:
                pass
            else:
                event_counter['unknown'] += 1

        return "unknown: %s, warning: %s, critical: %s" % (event_counter['unknown'],event_counter['warning'],event_counter['critical'])

    @botcmd(split_args_with=None)
    def sensu_summarize(self, mess, args):
        api = self.resolve_endpoint(args[0])
        return self.summarize_events(api)

    @botcmd(split_args_with=None)
    def sensu_silence(self, mess, args):
        owner = mess.getFrom().getStripped()
        api = self.resolve_endpoint(args[0])
        path = args[1]
        expires = None
        return silence(api, owner, path, expires)

    @botcmd(split_args_with=None)
    def sensu_unsilence(self, mess, args):
        api = self.resolve_endpoint(args[0])
        path = args[1]
        return unsilence(api, path)

    @botcmd(split_args_with=None)
    def sensu_stashlist(self, mess, args):
        api = self.resolve_endpoint(args[0])
        result = get_stashes(api)
        if result == []:
            return "No stashes found"
        else:
            return result

    @botcmd(split_args_with=None)
    def sensu_silencelist(self, mess, args):
        api = self.resolve_endpoint(args[0])
        result = get_silenced(api)
        if result == []:
            return "No silenced clients/checks found"
        else:
            return result





