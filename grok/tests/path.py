import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
import grok
import unittest

class PathPatternsTest(unittest.TestCase):
  def setUp(self):
      self.grok = grok.Grok()
      path = os.path.dirname(os.path.abspath(__file__)) + '/../patterns/base'
      self.grok.add_patterns_from_file(path)
      self.grok.compile("%{PATH}")

  def test_unix_paths(self):
    paths = ['/', '/usr', '/usr/bin', '/usr/bin/foo', '/etc/motd', '/home/.test',
             '/foo/bar//baz', '//testing', '/.test', '/%foo%', '/asdf/asdf,v']
    for path in paths:
      match = self.grok.match(path)
      self.assertNotEqual(False, match)
      self.assertEqual(path, match.captures["PATH"][0])

  def test_windows_paths(self):
    paths = [r'C:\WINDOWS' r'\\\\Foo\bar' r'\\\\1.2.3.4\C$' r'\\\\some\path\here.exe',
             'C:\\Documents and Settings\\']
    for path in paths:
      match = self.grok.match(path)
      self.assertNotEqual(False, match, "Expected %s to match, but it didn't." % path)
      self.assertEqual(path, match.captures["PATH"][0])


if __name__ == '__main__':
    unittest.main()
