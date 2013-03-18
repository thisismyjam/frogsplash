import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
import grok
import unittest

class GrokBasicTests(unittest.TestCase):
  def setUp(self):
      self.grok = grok.Grok()

  def test_grok_compile_fails_on_invalid_expressions(self):
    bad_regexps = ["[", "[foo", "?", "(?-"]
    for regexp in bad_regexps:
        self.assertRaises(Exception, self.grok.compile, regexp)
                          

  def test_grok_compile_succeeds_on_valid_expressions(self):
    good_regexps = ["[hello]", "(test)", "(?:hello)", "(?=testing)"]
    for regexp in good_regexps:
        self.grok.compile(regexp)

  def test_grok_pattern_is_same_as_compile_pattern(self):
    pattern = "Hello world"
    self.grok.compile(pattern)
    self.assertEqual(pattern, self.grok.pattern)

  # TODO(sissel): Move this test to a separate test suite aimed
  # at testing grok internals
  def test_grok_expanded_pattern_works_correctly(self):
    self.grok.add_pattern("test", "hello world")
    self.grok.compile("%{test}")
    self.assertEqual("(?<a0>hello world)", self.grok.expanded_pattern)

  def test_grok_expanded_unknown_pattern(self):
    self.assertRaises(grok.PatternError, self.grok.compile, "%{foo}")

  def test_grok_expanded_unknown_pattern_embedded(self):
    self.grok.add_pattern("test", "hello world")
    self.assertRaises(grok.PatternError, self.grok.compile, "%{test} bar %{foo} baz")
                      


if __name__ == '__main__':
    unittest.main()
