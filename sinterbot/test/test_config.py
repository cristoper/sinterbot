import unittest
import sinterbot.algorithms as algo
import sinterbot.sinterconf as config

class TestParse(unittest.TestCase):
    def test_successful_parse(self):
        c = config.SinterConf.parse_and_validate('sample.conf')
        self.assertEqual(c.smtpserver, 'smtp.email.tld')
        self.assertEqual(c.smtpuser, 'smtpuser@email.tld')
        self.assertEqual(c.smtppass, 'secret')
        self.assertEqual(c.smtpport, '587')
        self.assertEqual(c.m, 1)
        self.assertEqual(len(c.bl.list), 2)
        self.assertEqual(len(c.santas.santas), 5)
        self.assertEqual(len(c.santas.emails()), 5)

    def test_wrong_blacklist(self):
        """Test that typo in blacklist raises exception"""
        with self.assertRaises(config.ValidateError):
            config.SinterConf.parse_and_validate('sinterbot/test/wrongbl.conf')

    def test_missing_colon(self):
        """Test that malformed config file raises exception"""
        with self.assertRaises(config.ParseError) as err:
            c = config.SinterConf('sinterbot/test/malformed.conf')
            c.parse()
        self.assertEqual(err.exception.line, 7)

class TestDerange(unittest.TestCase):
    def test_random_all(self):
        c = config.SinterConf.parse_and_validate('sample.conf')
        p = c.derange()
        c.validate()
        self.assertEqual(len(p), 5)
        print(p, algo.decompose(p))


if __name__ == '__main__':
    unittest.main()
