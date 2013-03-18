import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
import grok
import unittest

class QuotedStringPatternsTest(unittest.TestCase):
  def setUp(self):
      self.grok = grok.Grok()
      path = os.path.dirname(os.path.abspath(__file__)) + '/../patterns/base'
      self.grok.add_patterns_from_file(path)
      self.grok.compile("^%{PROG}$")

  def test_quoted_string_common(self):
    self.grok.compile("%{QUOTEDSTRING}")
    inputs = ["hello", ""]
    quotes = ['"', "'", '`']
    for value in inputs:
      for quote in quotes:
        str = "%s%s%s" % (quote, value, quote)
        match = self.grok.match(str)
        self.assertNotEqual(False, match)
        self.assertEqual(str, match.captures["QUOTEDSTRING"][0])

  def test_quoted_string_inside_escape(self):
    self.grok.compile("%{QUOTEDSTRING}")
    quotes = ['"', "'", '`']
    for quote in quotes:
      str = "%shello \\%sworld\\%s%s" % tuple([quote] * 4)
      match = self.grok.match(str)
      self.assertNotEqual(False, match)
      self.assertEqual(str, match.captures["QUOTEDSTRING"][0])

  def test_escaped_quotes_no_match_quoted_string(self):
    self.grok.compile("%{QUOTEDSTRING}")
    inputs = ["\\\"testing\\\"", "\\\'testing\\\'", "\\`testing\\`",]
    for value in inputs:
      match = self.grok.match(value)
      self.assertEqual(False, match)

  def test_non_quoted_strings_no_match(self):
    self.grok.compile("%{QUOTEDSTRING}")
    inputs = ["\\\"testing", "testing", "hello world ' something ` foo"]
    for value in inputs:
      match = self.grok.match(value)
      self.assertEqual(False, match)


if __name__ == '__main__':
    unittest.main()
