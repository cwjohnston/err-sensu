# err-sensu

A plugin for [Err](https://github.com/gbin/err) which interacts with [Sensu](http://sensuapp.com) API endpoints.

## Config

The plugin takes a list of Sensu API endpoints with a named environment, like so:

`!config Sensu {'ENDPOINTS': [{'ENVIRONMENT': 'staging', 'URI': 'http://sensu.staging.example.com'}]}`

## Usage

Each sensu command expects the endpoint environment name as its first argument, e.g. `!sensu qa summarize` would attempt to summarize events from the Sensu API endpoint whose `ENVIRONMENT` is 'qa'.

### Commands
* `silence` - silence a client or client/check
* `unsilence` - unsilence a client or client/check
* `silencelist` - list silenced clients/checks
* `stashlist` - list all stashes including those used for silencing
* `summarize` - print a summary of events by severity

## License

Released into public domain. Do with it as you wish!
