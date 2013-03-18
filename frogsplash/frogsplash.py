import argparse
import pyinotify
import os
import sys
import json
import pyes
import datetime
import stat
import socket
from grok import Grok

def die(message):
    sys.stderr.write(message + '\n')
    sys.exit(1)

class Tail(object):

    def __init__(self, filename, callback):
        self.filename = os.path.abspath(filename)
        if not os.path.exists(self.filename):
            die('No such file: %s' % filename)
        if not os.path.isfile(self.filename):
            die('Not a file: %s' % filename)

        self.f = open(filename, 'r')
        self.f.seek(0, 2)
        self.callback = callback

        watch_manager = pyinotify.WatchManager()
        notifier = pyinotify.Notifier(watch_manager, Tail.ProcessEvent(self))
        dirmask = pyinotify.IN_MODIFY | pyinotify.IN_CREATE
        watch_manager.add_watch(os.path.dirname(self.filename), dirmask)
 
        while True:
            notifier.process_events()
            if notifier.check_events():
                notifier.read_events()

    def check_truncate(self):
        if os.stat(self.filename)[stat.ST_SIZE] < self.f.tell():
            sys.stderr.write('Log file truncated\n')
            self.f.seek(0)

    def reopen(self):
        self.f.close()
        self.f = open(self.filename, 'r')

    def lines_added(self):
        while True:
            line = self.f.readline()
            if not line:
                break
            line = line.split('\n')[0]
            self.callback(line)

    class ProcessEvent(pyinotify.ProcessEvent):

        def __init__(self, tail):
            self.tail = tail

        def process_IN_MODIFY(self, event):
            if self.tail.filename != event.path + '/' + event.name:
                return

            self.tail.lines_added()
            self.tail.check_truncate()

        def process_IN_CREATE(self, event):
            if self.tail.filename != event.path + '/' + event.name:
                return
            sys.stderr.write('Log file re-created, re-opening\n')
            self.tail.reopen()
            self.tail.lines_added()
            #self.tail.file.seek(0, 2) # TODO: is this necessary?
            
def make_groks(patterns):
    groks = []
    for pattern in patterns:
        grok = Grok()
        grok.add_base_patterns()
        grok.compile(pattern)
        groks.append(grok)
    return groks

def groks_match(groks, line):
    for grok in groks:
        match = grok.match(line)
        if match:
            return match
    return False

def debug_match(fields):
    print json.dumps(fields)

def send_to_elastic_search(es, fields, message, log_type, source):
    now = datetime.datetime.now()
    index = {
        '@timestamp': now.isoformat(),
        '@source': source,
        '@fields': 
            dict((key, ','.join(value)) for key, value in fields.items())
            ,
        '@message': message
        }
    es.index(index, 'logstash-%s' % now.strftime('%Y.%m.%d'), log_type)

def frogsplash(elastic_host, elastic_port, filename, patterns, log_type, source,
               verbose, dry_run):
    groks = make_groks(patterns)

    if not dry_run:
        es = pyes.ES('%s:%d' % (elastic_host, elastic_port))

    def handle_line(line):
        match = groks_match(groks, line)
        if not match:
            sys.stderr.write('Failed to match line: "%s"\n' % line)
            return
        if not dry_run:
            send_to_elastic_search(es, match.captures, match.subject, log_type, source)
        if verbose:
            debug_match(match.captures)

    tail = Tail(filename, handle_line)

def main():
    parser = argparse.ArgumentParser(description='Tail file; grok; send to Elasticsearch in logstash format')
    parser.add_argument('-H', '--host', default='localhost',
                        help='Elasticsearch host')
    parser.add_argument('-p', '--port', default=9200, type=int,
                        help='Elasticsearch port')
    parser.add_argument('-v', '--verbose', default=False, action='store_true')
    parser.add_argument('-d', '--dry-run', default=False, action='store_true')
    parser.add_argument('-t', '--type', default='default',
                        help='"type", as sent to Elasticsearch')
    parser.add_argument('-s', '--source', default=socket.gethostname(),
                        help='"source", as sent to Elasticsearch')
    parser.add_argument('-g', '--grok', action='append', required=True,
                        help='Grok pattern to match, can be used multiple times')
    parser.add_argument('file', help='Log file to tail')
                        
    args = parser.parse_args()
    frogsplash(args.host, args.port, args.file, args.grok, args.type, args.source,
               args.verbose, args.dry_run)

if __name__ == '__main__':
    main()
