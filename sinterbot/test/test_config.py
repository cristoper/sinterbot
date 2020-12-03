import unittest
import sinterbot.sinterconf as config
import sinterbot.smtpconf as smtpconfig

class TestParseSMTP(unittest.TestCase):
    def test_successful_parse(self):
        c = smtpconfig.SMTPConf('smtpsample.conf')
        c.parse()
        self.assertEqual(c.server, 'smtp.email.tld')
        self.assertEqual(c.user, 'smtpuser@email.tld')
        self.assertEqual(c.password, 'secret')
        self.assertEqual(c.port, '587')

class TestParse(unittest.TestCase):
    def test_successful_parse(self):
        c = config.SinterConf.parse_and_validate('sample.conf')
        self.assertEqual(c.mincycle, 3)
        self.assertEqual(len(c.bl.list), 2)
        self.assertEqual(len(c.santas.santas), 5)
        self.assertEqual(len(c.santas.emails()), 5)

    def test_wrong_blacklist(self):
        """Test that typo in blacklist raises exception"""
        with self.assertRaises(config.ValidateError):
            config.SinterConf.parse_and_validate('sinterbot/test/wrongbl.conf')

    def test_big_mincycle(self):
        """Test that a mincycle > n will not validate"""
        with self.assertRaises(config.ValidateError):
            c = config.SinterConf.parse_and_validate('sinterbot/test/bigm.conf')


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


if __name__ == '__main__':
    unittest.main()
