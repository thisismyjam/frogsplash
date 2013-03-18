import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
import grok
import unittest

class IPPatternsTest(unittest.TestCase):
  def setUp(self):
      self.grok = grok.Grok()
      path = os.path.dirname(os.path.abspath(__file__)) + '/../patterns/base'
      self.grok.add_patterns_from_file(path)

  def test_ips(self):
    self.grok.compile("%{IP}")
    with open('ip.input', 'r') as f:
        for line in f.readlines():
            line = line.strip()
            match = self.grok.match(line)
            self.assertNotEqual(False, match)
            self.assertEqual(line, match.captures["IP"][0])

  def test_non_ips(self):
    self.grok.compile("%{IP}")
    nonips = ['255.255.255.256', '0.1.a.33', '300.1.2.3', '300', '400.4.3.a', '1.2.3.b',
               '1..3.4.5', 'hello', 'world', 'hello world']
    for input in nonips:
      match = self.grok.match(input)
      self.assertEqual(False, match)


if __name__ == '__main__':
    unittest.main()
