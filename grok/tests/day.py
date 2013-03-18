import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
import grok
import unittest

class DayPatternsTest(unittest.TestCase):
  def setUp(self):
      self.grok = grok.Grok()
      path = os.path.dirname(os.path.abspath(__file__)) + '/../patterns/base'
      self.grok.add_patterns_from_file(path)
      self.grok.compile("%{DAY}")

  def test_days(self):
    for day in ['Mon', 'Monday', 'Tue', 'Tuesday', 'Wed', 'Wednesday', 'Thu',
                'Thursday', 'Fri', 'Friday', 'Sat', 'Saturday', 'Sun', 'Sunday']:
      match = self.grok.match(day)
      self.assertNotEqual(False, day, "Expected #{day} to match.")
      self.assertEqual(day, match.captures["DAY"][0])


if __name__ == '__main__':
    unittest.main()
