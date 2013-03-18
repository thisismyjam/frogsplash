Frogsplash
==========

Frogsplash is rhyming slang for Minimal [Logstash](http://www.logstash.net).
It tries to satisfy the minimum use case of tailing a log file, parsing it with
[grok](http://code.google.com/p/semicomplete/wiki/GrokConcepts), and indexing in 
ElasticSearch (using Logstash's [format](https://github.com/logstash/logstash/wiki/logstash%27s-internal-message-format), which can be read by tools like [Kibana](http://kibana.org/)).

![logo](https://raw.github.com/andreasjansson/frogsplash/master/logo.png)

Installation
------------

    sudo setup.py install

Usage
-----

    frogsplash [-H HOST] [-p PORT] [-v] [-d] [-t TYPE] [-s SOURCE] -g GROK file

where

 * -H, --host is the ElasticSearch host
 * -p, --port is the ElasticSearch port
 * -v, --verbose enables verbose output
 * -d, --dry-run dry-runs FrogSplash, meaning it won't send anything to ElasticSearch
 * -t, --type is the "type", as sent to ElasticSearch
 * -s, --source is the "source", as sent to ElasticSearch
 * -g, --grok is a grok pattern (you can use this parameter more than once for multiple patterns, but only the first match will be used)

Caveats
-------

Frogsplash uses [inotify](https://github.com/seb-m/pyinotify/wiki) to tail
log files, so Linux is (currently) the only supported platform.

Instead of [re](http://docs.python.org/2/library/re.html), it uses the experimental [regex](https://pypi.python.org/pypi/regex) module. So far I haven't encountered any problems, but there may be bugs.
