import json
from errbot import BotPlugin, botcmd
from collections import Counter

from sensu import get_events, get_stashes, get_stale_stashes, silence, unsilence


class Sensu(BotPlugin):
    """An Err plugin Sensu"""
    min_err_version = '1.6.0'  # Optional, but recommended
    max_err_version = '2.0.0'  # Optional, but recommended

    def announce_stale_stashes(self, config, stale_after):
        stale_stashes = get_stale_stashes(config['URI'], stale_after)
        stale_stash_names = []
        for stash in stale_stashes:
            stripped_name = stash['path'].replace('silence/', '')
            stale_stash_names.append(stripped_name)

        return "Stale stashes in %s : %s" % (config['ENVIRONMENT'], ', '.join(stale_stash_names))

    def get_configuration_template(self):
        """Defines the configuration structure this plugin supports"""
        return {'ENDPOINTS': [{'ENVIRONMENT': 'staging', 'URI': 'http://sensu.staging.example.com'}]}

    def resolve_endpoint(self, env):
        """ Returns endpoint configuration dict"""
        endpoint_config = None
        for endpoint in self.config['ENDPOINTS']:
            if endpoint['ENVIRONMENT'] == env:
                endpoint_config = endpoint
                break
            else:
                pass

        if endpoint_config is None:
            raise Exception('Sorry, I could not match your request to a known API endpoint')
        else:
            return endpoint_config

    def summarize_events(self, uri):
        events = get_events(uri)
        event_counter = Counter()

        for event in events:
            if event['flapping'] is True:
                event_counter['flapping'] += 1
            if event['status'] == 2:
                event_counter['critical'] += 1
            elif event['status'] == 1:
                event_counter['warning'] += 1
            elif event['status'] == 0:
                pass
            else:
                event_counter['unknown'] += 1

        return "unknown: %s, warning: %s, critical: %s" % (event_counter['unknown'], event_counter['warning'], event_counter['critical'])

    @botcmd(split_args_with=None)
    def sensu_summarize(self, mess, args):
        config = self.resolve_endpoint(args[0])
        return self.summarize_events(config['URI'])

    @botcmd(split_args_with=None)
    def sensu_silence(self, mess, args):
        owner = mess.getFrom().getStripped()
        config = self.resolve_endpoint(args[0])

        if args[2]:
            path = args[1]
        else:
            return "Sorry, you need to specify the path for me to silence"

        if args[2]:
            try:
                duration = int(args[2])
            except ValueError:
                return "Sorry, I couldn't turn %s into an integer" % (args[2],)
        else:
            duration = None

        result = silence(config['URI'], owner, path, duration)

        if 'path' in result:
            return "Silenced %s for %s minutes" % (result['path'].replace('silence/', ''), duration,)
        else:
            return "Sorry, something unexpected happened: %s" % (json.dumps(result),)

    @botcmd(split_args_with=None)
    def sensu_unsilence(self, mess, args):
        config = self.resolve_endpoint(args[0])
        path = args[1]
        result = unsilence(config['URI'], path)

        if len(result) == 0:
            return "Unsilenced  %s" % (path.replace('silence/', ''),)
        else:
            return "Sorry, something unexpected happened: %s" % (json.dumps(result),)

    @botcmd(split_args_with=None)
    def sensu_stashlist(self, mess, args):
        config = self.resolve_endpoint(args[0])
        result = get_stashes(config['URI'])
        if result == []:
            return "No stashes found"
        else:
            return result

    @botcmd(split_args_with=None)
    def sensu_silencelist(self, mess, args):
        config = self.resolve_endpoint(args[0])
        result = get_stashes(config['URI'])
        if result == []:
            return "No silenced clients/checks found"
        else:
            return result

    @botcmd(split_args_with=None)
    def sensu_stalestashlist(self, mess, args):
        config = self.resolve_endpoint(args[0])
        if len(args) > 1:
            stale_after = int(args[1])
        else:
            stale_after = 30

        stale_stashes = get_stale_stashes(config['URI'], stale_after)
        stale_stash_names = []
        for stash in stale_stashes:
            stripped_name = stash['path'].replace('silence/', '')
            stale_stash_names.append(stripped_name)

        return "Stale stashes in %s : %s" % (config['ENVIRONMENT'], ', '.join(stale_stash_names))
