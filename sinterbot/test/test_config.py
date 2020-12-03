import unittest
import shutil
import sinterbot.sinterconf as config
import sinterbot.smtpconf as smtpconfig

TESTDIR = 'sinterbot/test/'

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
        c = config.SinterConf.parse_and_validate(TESTDIR+'test.conf')
        self.assertEqual(c.mincycle, 3)
        self.assertEqual(len(c.bl.list), 2)
        self.assertEqual(len(c.santas.santas), 5)
        self.assertEqual(len(c.santas.emails()), 5)

    def test_wrong_blacklist(self):
        """Test that typo in blacklist raises exception"""
        with self.assertRaises(config.ValidateError):
            config.SinterConf.parse_and_validate(TESTDIR+'wrongbl.conf')

    def test_big_mincycle(self):
        """Test that a mincycle > n will not validate"""
        with self.assertRaises(config.ValidateError):
            config.SinterConf.parse_and_validate(TESTDIR+'bigm.conf')

    def test_missing_colon(self):
        """Test that malformed config file raises exception"""
        with self.assertRaises(config.ParseError) as err:
            c = config.SinterConf(TESTDIR+'malformed.conf')
            c.parse()
        self.assertEqual(err.exception.line, 7)

class TestDerangeSave(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # copy test.conf so we can modify it and test that it worked
        shutil.copy(TESTDIR+'test.conf', TESTDIR+'test.deranged')

    def test_save_derangement(self):
        """
        Creates, saves, then reads a derangement file and asserts that it is
        equal to the deranged input config file.
        """
        c = config.SinterConf.parse_and_validate(TESTDIR+'test.conf')
        p = c.derange()
        c.validate()
        self.assertEqual(len(p), 5)
        c.save_derangement()
        d = config.SinterConf.parse_and_validate(TESTDIR+'test.deranged')
        self.assertEqual(c.mincycle, d.mincycle)
        self.assertEqual(len(c.bl), len(d.bl))
        for i in range(len(c.bl)):
            self.assertEqual(c.bl[i], d.bl[i])
        self.assertEqual(len(c.santas), len(d.santas))
        for i in range(len(c.santas)):
            self.assertEqual(c.santas[i].email, d.santas[i].email)
        self.assertEqual(c.derangement, d.derangement)

    def test_wrong_derangement(self):
        """
        Test that a .deranged file with a wrong derangement fails validation.
        """
        with self.assertRaises(config.ValidateError):
            config.SinterConf.parse_and_validate(TESTDIR+'badderangement.conf')

    def test_missing_santa(self):
        """
        Test that a .deranged file with a missing santa fails validation.
        """
        with self.assertRaises(config.ValidateError):
            config.SinterConf.parse_and_validate(TESTDIR+'missingemail.derangement')



if __name__ == '__main__':
    unittest.main()
