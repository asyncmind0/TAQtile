from os.path import expanduser
import subprocess
try:
    from builtins import str
except Exception as e:
    from future.builtins import str

from libqtile.widget import base
from libqtile.log_utils import logger as log

from .bank import CommBank


class BankBalance(base.ThreadedPollText):
    defaults = [
        ('warning', 300, 'Warning limit.'),
        ('warning_foreground', '#FF0000', 'Warning Color - no updates.'),
        ('warning_background', '', 'Warning Color - no updates.'),
        ('critical', 100, 'Critical limit.'),
        ('critical_foreground', '#FF0000', 'Warning Color - no updates.'),
        ('critical_background', '#FFffff', 'Critical Color - no updates.'),
        ('unavailable', '#ffffff', 'Unavailable Color - no updates.'),
        ("account", "debit", "Which account to show (all/0/1/2/...)"),
    ]
    fixed_upper_bound = False
    amount = None
    CACHE = {}

    def __init__(self, **config):
        # graph._Graph.__init__(self, **config)
        base.ThreadedPollText.__init__(self, **config)
        self.add_defaults(BankBalance.defaults)

    def draw(self):
        foreground = self.foreground
        background = self.background
        if self.amount is None:
            return
        try:
            if float(self.amount) <= self.critical:
                background = self.critical_background
                foreground = self.critical_foreground
            elif float(self.amount) <= self.warning:
                background = self.warning_background
                foreground = self.warning_foreground
        except ValueError as e:
            log.exception("Draw error")
        except Exception as e:
            log.exception("Draw error")
        self.foreground = foreground
        self.background = background
        base.ThreadedPollText.draw(self)

    def poll(self, data=None):
        text = "$$$$"
        user = None
        try:
            user = subprocess.check_output(
                ['pass', "financial/commbank/debit/user"]).strip().decode('utf8')
            password = subprocess.check_output(
                ['pass', "financial/commbank/debit/pass"]).strip().decode('utf8')
            log.warning("BankBalance:%s", user)
            commbank = CommBank(user, password)
            self.data = data = commbank.data
            if self.account == 'credit':
                self.amount = commbank.get_currency(
                    commbank.data['AccountGroups'][0]['ListAccount'][-2]['AvailableFunds']
                )
            else:
                self.amount = commbank.get_currency(
                    commbank.data['AccountGroups'][0]['ListAccount'][0]['AvailableFunds']
                )
            text = "%s%s" % (
                self.amount,
                'C' if self.account == 'credit' else 'D',
            )
            log.warning("BankBalance:%s", text)
        except Exception as e:
            log.exception("BankBalance: %s %s", user, data)
        # text = commbank.net_position
        return str(text)

    def button_press(self, x, y, button):
        subprocess.check_output(
            'notify-send %s' %
            str(
                subprocess.check_output(
                    [
                        'python',
                        expanduser("~/.bin/bank.py"),
                    ]).strip().decode('utf8')
            )
        )
