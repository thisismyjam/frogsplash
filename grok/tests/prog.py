import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
import grok
import unittest

class ProgPatternsTest(unittest.TestCase):
  def setUp(self):
      self.grok = grok.Grok()
      path = os.path.dirname(os.path.abspath(__file__)) + '/../patterns/base'
      self.grok.add_patterns_from_file(path)
      self.grok.compile("^%{PROG}$")

  def test_progs(self):
    progs = ['kernel', 'foo-bar', 'foo_bar', 'foo/bar/baz']
    for prog in progs:
      match = self.grok.match(prog)
      self.assertNotEqual(False, prog, "Expected %s to match." % prog)
      self.assertEqual(prog, match.captures["PROG"][0], "Expected #{prog} to match capture.")


if __name__ == '__main__':
    unittest.main()
