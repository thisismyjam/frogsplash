import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
import grok
import unittest

class URIPatternsTest(unittest.TestCase):
  def setUp(self):
      self.grok = grok.Grok()
      path = os.path.dirname(os.path.abspath(__file__)) + '/../patterns/base'
      self.grok.add_patterns_from_file(path)
      self.grok.compile("%{URI}")

  def test_urls(self):
    urls = ["http://www.google.com", "telnet://helloworld",
            "http://www.example.com/", "http://www.example.com/test.html", 
            "http://www.example.com/test.html?foo=bar", 
            "http://www.example.com/test.html?foo=bar&fizzle=baz", 
            "http://www.example.com:80/test.html?foo=bar&fizzle=baz", 
            "https://www.example.com:443/test.html?foo=bar&fizzle=baz", 
            "https://user@www.example.com:443/test.html?foo=bar&fizzle=baz", 
            "https://user:pass@somehost/fetch.pl",
            "puppet:///",
            "http://www.foo.com",
            "http://www.foo.com/",
            "http://www.foo.com/?testing",
            "http://www.foo.com/?one=two",
            "http://www.foo.com/?one=two&foo=bar",
            "foo://somehost.com:12345",
            "foo://user@somehost.com:12345",
            "foo://user@somehost.com:12345/",
            "foo://user@somehost.com:12345/foo.bar/baz/fizz",
            "foo://user@somehost.com:12345/foo.bar/baz/fizz?test",
            "foo://user@somehost.com:12345/foo.bar/baz/fizz?test=1&sink&foo=4",
            "http://www.google.com/search?hl=en&source=hp&q=hello+world+%5E%40%23%24&btnG=Google+Search",
            "http://www.freebsd.org/cgi/url.cgi?ports/sysutils/grok/pkg-descr",
            "http://www.google.com/search?q=CAPTCHA+ssh&start=0&ie=utf-8&oe=utf-8&client=firefox-a&rls=org.mozilla:en-US:official",
            "svn+ssh://somehost:12345/testing",
           ]
            
    for url in urls:
      match = self.grok.match(url)
      self.assertNotEqual(False, match, "Expected this to match: #{url}")
      self.assertEqual(url, match.captures["URI"][0])


if __name__ == '__main__':
    unittest.main()
