import unittest
import sinterbot.config

class TestParse(unittest.TestCase):
    def test_successful_parse(self):
        c = sinterbot.config.ConfFile('sample.conf')
        self.assertEqual(c.smtpserver, 'smtp.email.tld')
        self.assertEqual(c.smtpuser, 'smtpuser@email.tld')
        self.assertEqual(c.smtppass, 'secret')
        self.assertEqual(c.smtpport, '587')
        self.assertEqual(int(c.m), 1)
        self.assertEqual(len(c.bl.get_bl()), 2)
        self.assertEqual(len(c.santas), 5)

    def test_missing_colon(self):
        """Test that malformed config file raises exception"""
        with self.assertRaises(sinterbot.config.ParseError) as err:
            sinterbot.config.ConfFile('sinterbot/test/malformed.conf')
        self.assertEqual(err.exception.line, 7)


if __name__ == '__main__':
    unittest.main()
