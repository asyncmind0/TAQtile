from unittest import TestCase
from .bankbalance import BankBalance
import re


class BankBalanceTest(TestCase):
    def test_poll(self):
        bb = BankBalance()
        result = bb.poll()
        self.assertTrue(re.match("\d+\.\d+C|\d+\.\d+D", result), result)
