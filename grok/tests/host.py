import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
import grok
import unittest
import random

class HostPattternTest(unittest.TestCase):
  def setUp(self):
      self.grok = grok.Grok()
      path = os.path.dirname(os.path.abspath(__file__)) + '/../patterns/base'
      self.grok.add_patterns_from_file(path)
      self.grok.compile("%{HOSTNAME}")

  def test_hosts(self):
    hosts = ["www.google.com", "foo-234.14.AAc5-2.foobar.net",
            "192-455.a.b.c.d."]
    for host in hosts:
      match = self.grok.match(host)
      self.assertNotEqual(False, match, "Expected this to match: #{host}")
      self.assertEqual(host, match.captures["HOSTNAME"][0])



if __name__ == '__main__':
    unittest.main()
