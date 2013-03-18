import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
import grok
import unittest

class GrokPatternCapturingTests(unittest.TestCase):
  def setUp(self):
    self.grok = grok.Grok()

  def test_basic_capture(self):
    self.grok.add_pattern("foo", ".*")
    self.grok.compile("%{foo}")
    input = "hello world"
    match = self.grok.match(input)
    self.assertEqual("(?P<a0>.*)", self.grok.expanded_pattern)
    self.assertEqual(1, len(match.captures))
    self.assertEqual(1, len(match.captures["foo"]))
    self.assertEqual(input, match.captures["foo"][0])

    self.assertEqual(0, match.start,
                      "Match of /.*/, start should equal 0")
    self.assertEqual(len(input), match.end,
                      "Match of /.*/, end should equal input string length")
    self.assertEqual(input, match.subject)

  def test_multiple_captures_with_same_name(self):
    self.grok.add_pattern("foo", "\\w+")
    self.grok.compile("%{foo} %{foo}")
    match = self.grok.match("hello world")
    self.assertNotEqual(False, match)
    self.assertEqual(1, len(match.captures))
    self.assertEqual(2, len(match.captures["foo"]))
    self.assertEqual("hello", match.captures["foo"][0])
    self.assertEqual("world", match.captures["foo"][1])

  def test_multiple_captures(self):
    self.grok.add_pattern("foo", "\\w+")
    self.grok.add_pattern("bar", "\\w+")
    self.grok.compile("%{foo} %{bar}")
    match = self.grok.match("hello world")
    self.assertNotEqual(False, match)
    self.assertEqual(2, len(match.captures))
    self.assertEqual(1, len(match.captures["foo"]))
    self.assertEqual(1, len(match.captures["bar"]))
    self.assertEqual("hello", match.captures["foo"][0])
    self.assertEqual("world", match.captures["bar"][0])

  def test_nested_captures(self):
    self.grok.add_pattern("foo", "\\w+ %{bar}")
    self.grok.add_pattern("bar", "\\w+")
    self.grok.compile("%{foo}")
    match = self.grok.match("hello world")
    self.assertNotEqual(False, match)
    self.assertEqual(2, len(match.captures))
    self.assertEqual(1, len(match.captures["foo"]))
    self.assertEqual(1, len(match.captures["bar"]))
    self.assertEqual("hello world", match.captures["foo"][0])
    self.assertEqual("world", match.captures["bar"][0])

  def test_nesting_recursion(self):
    self.grok.add_pattern("foo", "%{foo}")
    self.assertRaises(grok.PatternError, self.grok.compile, "%{foo}")

  def test_inline_define(self):
    path = os.path.dirname(os.path.abspath(__file__)) + '/../patterns/base'
    self.grok.add_patterns_from_file(path)

    self.grok.compile(r"%{foo=%{IP} %{BASE10NUM:fizz}}")
    match = self.grok.match("1.2.3.4 300.4425")
    self.assertEqual(3, len(match.captures))
    self.assertTrue("foo" in match.captures)
    self.assertTrue("IP" in match.captures)
    self.assertTrue("BASE10NUM:fizz" in match.captures)


  def test_valid_capture_subnames(self):
    name = "foo"
    self.grok.add_pattern(name, "\\w+")
    subname = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_abc:def"
    self.grok.compile("%%{%s:%s}" % (name, subname))
    match = self.grok.match("hello")
    self.assertNotEqual(False, match)
    self.assertEqual(1, len(match.captures))
    self.assertEqual(1, len(match.captures["%s:%s" % (name, subname)]))
    self.assertEqual("hello", match.captures["%s:%s" % (name, subname)][0])

if __name__ == '__main__':
    unittest.main()
