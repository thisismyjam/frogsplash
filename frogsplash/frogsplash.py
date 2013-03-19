import argparse
import pyinotify
import os
import sys
import json
import pyes
import datetime
import stat
import socket
import threading
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


class Frogsplash(object):

    def __init__(self, elastic_host, elastic_port, filename, patterns, log_type, source,
                 multiline_patterns, verbose, dry_run):
        self.elastic_host = elastic_host
        self.elastic_port = elastic_port
        self.filename = filename
        self.groks = self.make_groks(patterns)
        self.log_type = log_type
        self.source = source
        if multiline_patterns:
            self.multiline_groks = self.make_groks(multiline_patterns)
            self.pending = None
            self.pending_timer = None
            self.pending_timeout = 5
        else:
            self.multiline_groks = None
        self.verbose = verbose
        self.dry_run = dry_run

        if not self.dry_run:
            self.es = pyes.ES('%s:%d' % (self.elastic_host, self.elastic_port))

        if self.multiline_groks:
            handle_line = self.handle_multiline
        else:
            handle_line = self.handle_line

        self.tail = Tail(self.filename, handle_line)

    def handle_line(self, line):
        match = self.groks_match(self.groks, line)
        if match:
            self.send_to_elastic_search(match.captures, match.subject)
        else:
            sys.stderr.write('Failed to match line: "%s"\n' % line)

    def send_pending(self):
        if self.pending:
            self.send_to_elastic_search(self.pending.captures, self.pending.subject)
            self.pending = None
        self.cancel_pending_timer()

    def cancel_pending_timer(self):
        if self.pending_timer:
            self.pending_timer.cancel()
            self.pending_timer = None

    def set_pending_timer(self):
        self.pending_timer = threading.Timer(self.pending_timeout, self.send_pending)
        self.pending_timer.start()

    def handle_multiline(self, line):
        self.cancel_pending_timer()

        if self.pending and self.groks_match_regex(self.multiline_groks, line):
            self.pending.subject += '\n' + line
            self.set_pending_timer()
            return

        self.send_pending()

        match = self.groks_match(self.groks, line)
        if match:
            self.pending = match
            self.set_pending_timer()
        else:
            sys.stderr.write('Failed to match line: "%s"\n' % line)

    def send_to_elastic_search(self, fields, message):
        now = datetime.datetime.now()
        data = {
            '@timestamp': now.isoformat(),
            '@source': self.source,
            '@type': self.log_type,
            '@fields': dict((key, ','.join(value)) for key, value in fields.items()),
            '@message': message
            }
        if not self.dry_run:
            index = 'logstash-%s' % now.strftime('%Y.%m.%d')
            self.es.index(data, index, self.log_type)
        if self.verbose:
            print json.dumps(data)

    def make_groks(self, patterns):
        groks = []
        for pattern in patterns:
            grok = Grok()
            grok.add_base_patterns()
            grok.compile(pattern)
            groks.append(grok)
        return groks

    def groks_match(self, groks, line):
        for grok in groks:
            match = grok.match(line)
            if match:
                return match
        return False

    def groks_match_regex(self, groks, line):
        for grok in groks:
            if grok.regex.search(line):
                return True
        return False


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
    parser.add_argument('-m', '--multiline', action='append', metavar='PATTERN',
                        help='If the (grok) pattern occurs, the line will be merged with the previous line. Only groks from the previous line will be sent to the server. Can be used multiple times')
    parser.add_argument('-g', '--grok', action='append', required=True, metavar='PATTERN',
                        help='Grok pattern to match, can be used multiple times')
    parser.add_argument('file', help='Log file to tail')
                        
    args = parser.parse_args()
    Frogsplash(args.host, args.port, args.file, args.grok, args.type, args.source,
               args.multiline, args.verbose, args.dry_run)

if __name__ == '__main__':
    main()
