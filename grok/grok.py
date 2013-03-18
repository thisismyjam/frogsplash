import regex
import os

class Grok(object):

    PATTERN_RE = regex.compile(r'''
    %\{   
       (?<name>
         (?<pattern>[A-z0-9]+)
         (?::(?<subname>[A-z0-9_:]+))?
       )
       (?:=(?<definition>
         (?:
           (?:[^{}\\]+|\\.+)+
           |
           (?<curly>\{(?:(?>[^{}]+|(?>\\[{}])+)|(\g<curly>))*\})+
         )+
       ))?
       [^}]*
     \}
     ''', regex.VERBOSE)

    def __init__(self):
        self.patterns = {}
        self.capture_map = {}
        self.regex = None
        self.expanded_regex = None

    def add_patterns_from_file(self, path):
        with open(path, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                # Skip comments
                if regex.match(r'^\s*#', line):
                    continue
                # File format is: NAME ' '+ PATTERN '\n'
                split = regex.sub(r'^\s*', '', line).split(None, 1)
                if len(split) < 2:
                    continue
                name, pattern = split
                self.add_pattern(name, pattern)

    def add_base_patterns(self):
        self.add_patterns_from_file(os.path.dirname(os.path.abspath(__file__)) +
                                    '/patterns/base')

    def add_pattern(self, name, pattern):
        self.patterns[name] = pattern

    def compile(self, pattern):
        iterations_left = 10000
        index = 0
        self.pattern = pattern
        self.expanded_pattern = pattern

        while True:
            if iterations_left == 0:
                raise PatternError('Deep recursion pattern of %s - expanded: %s' % (
                        pattern, self.expanded_pattern))

            iterations_left -= 1
            m = Grok.PATTERN_RE.search(self.expanded_pattern)
            if not m:
                break

            m_pattern = m.group('pattern')
            m_definition = m.group('definition')
            m_name = m.group('name')

            if m_definition:
                self.add_pattern(m_pattern, m_definition)

            if m_pattern in self.patterns:
                r = self.patterns[m_pattern]
                capture = 'a%s' % index
                replacement_pattern = '(?<%s>%s)' % (capture, r)
                self.expanded_pattern = self.expanded_pattern.replace(m.group(0), replacement_pattern, 1)

                self.capture_map[capture] = m_name

                index += 1

        self.regex = regex.compile(self.expanded_pattern)

    def match(self, text):
        text = str(text)
        matches = self.regex.finditer(text)

        if matches:
            grokmatch = Match(text, matches, self)
            if grokmatch.captures:
                return grokmatch
        return False

    def capture_name(self, id):
        return self.capture_map[id]



class Match(object):

    def __init__(self, text, matches, grok):
        self.subject = text
        self.match = matches
        self.start = len(text)
        self.end = 0
        self.grok = grok

        self.captures = {}
        for match in matches:
            for key, string in sorted(match.groupdict().items()):

                # discard empty matches
                if not string:
                    continue

                name = self.grok.capture_name(key)

                if name in self.captures:
                    self.captures[name].append(string)
                else:
                    self.captures[name] = [string]

                if match.start() < self.start:
                    self.start = match.start()
                if match.end() > self.end:
                    self.end = match.end()


class PatternError(Exception):
    pass
