import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
import grok
import unittest
import random

class NumberPatternsTest(unittest.TestCase):
  def setUp(self):
      self.grok = grok.Grok()
      path = os.path.dirname(os.path.abspath(__file__)) + '/../patterns/base'
      self.grok.add_patterns_from_file(path)

  def test_match_number(self):
    self.grok.compile("%{NUMBER}")
    # step of a prime number near 100 so we get about 2000 iterations
    #puts self.grok.expanded_pattern.inspect
    for value in xrange(-100000, 1000000, 97):
      match = self.grok.match(str(value))
      self.assertNotEqual(False, match, "%s should not match false" % value)
      self.assertEqual(str(value), match.captures["NUMBER"][0])


  def test_match_number_float(self):
    # generate some random floating point values
    # always seed with the same random number, so the test is always the same
    self.grok.compile("%{NUMBER}")
    for value in xrange(0, 1000):
      value = str(random.uniform(-50000, 50000))
      match = self.grok.match(value)
      self.assertNotEqual(False, match)
      self.assertEqual(value, match.captures["NUMBER"][0])

  def test_match_number_amid_things(self):
    self.grok.compile("%{NUMBER}")
    value = "hello 12345 world"
    match = self.grok.match(value)
    self.assertNotEqual(False, match)
    self.assertEqual("12345", match.captures["NUMBER"][0])

    value = "Something costs $55.4!"
    match = self.grok.match(value)
    self.assertNotEqual(False, match)
    self.assertEqual("55.4", match.captures["NUMBER"][0])

  def test_no_match_number(self):
    self.grok.compile("%{NUMBER}")
    for value in ["foo", "", " ", ".", "hello world", "-abcd"]:
      match = self.grok.match(str(value))
      self.assertEqual(False, match)

  def test_match_base16num(self):
    self.grok.compile("%{BASE16NUM}")
    # Ruby represents negative values in a strange way, so only
    # test positive numbers for now.
    # I don't think anyone uses negative values in hex anyway...
    for value in xrange(0, 1000):
      for hexstr in [("%x" % value), ("0x%08x" % value), ("%016x" % value)]:
        match = self.grok.match(hexstr)
        self.assertNotEqual(False, match)
        self.assertEqual(hexstr, match.captures["BASE16NUM"][0])


if __name__ == '__main__':
    unittest.main()
