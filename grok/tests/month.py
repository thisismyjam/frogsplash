import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
import grok
import unittest

class MonthPatternsTest(unittest.TestCase):
  def setUp(self):
      self.grok = grok.Grok()
      path = os.path.dirname(os.path.abspath(__file__)) + '/../patterns/base'
      self.grok.add_patterns_from_file(path)
      self.grok.compile("%{MONTH}")

  def test_months(self):
    months = ["Jan", "January", "Feb", "February", "Mar", "March", "Apr",
              "April", "May", "Jun", "June", "Jul", "July", "Aug", "August",
              "Sep", "September", "Oct", "October", "Nov", "November", "Dec",
              "December"]
    for month in months:
      match = self.grok.match(month)
      self.assertNotEqual(False, match, "Expected %s to match" % month)
      self.assertEqual(month, match.captures["MONTH"][0])


if __name__ == '__main__':
    unittest.main()
