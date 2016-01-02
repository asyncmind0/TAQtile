from os.path import expanduser
import subprocess
import logging
try:
    from builtins import str
except Exception as e:
    from future.builtins import str

from libqtile.widget import base

from .bank import CommBank

log = logging.getLogger("qtile_%s" % __file__)

class BankBalance(base.ThreadedPollText):
    defaults = [
        ('warning', 300, 'Warning limit.'),
        ('warning_foreground', '#FF0000', 'Warning Color - no updates.'),
        ('warning_background', '', 'Warning Color - no updates.'),
        ('critical', 100, 'Critical limit.'),
        ('critical_foreground', '#FF0000', 'Warning Color - no updates.'),
        ('critical_background', '#FFffff', 'Critical Color - no updates.'),
        ('unavailable', '#ffffff', 'Unavailable Color - no updates.'),
        ("account", "all", "Which account to show (all/0/1/2/...)"),
    ]
    fixed_upper_bound = False

    def __init__(self, **config):
        # graph._Graph.__init__(self, **config)
        base.ThreadedPollText.__init__(self, **config)
        self.add_defaults(BankBalance.defaults)

    def draw(self):
        try:
            foreground = self.foreground
            background = self.background
            if float(self.text) <= self.warning:
                background = self.warning_background
                foreground = self.warning_foreground
            elif float(self.text) <= self.critical:
                background = self.critical_background
                foreground = self.critical_foreground
            self.foreground = foreground
            self.background = background
        except ValueError as e:
            pass
        except Exception as e:
            log.exception("Draw error")
        base.ThreadedPollText.draw(self)

    def poll(self, data=None):
        text = "$$$$"
        try:
            user = subprocess.check_output(
                ['pass', "financial/commbank/debit/user"]).strip().decode('utf8')
            password = subprocess.check_output(
                ['pass', "financial/commbank/debit/pass"]).strip().decode('utf8')
            log.warning("BankBalance:%s", user)
            commbank = CommBank(user, password)
            self.data = data = commbank.data
            credit = commbank.get_currency(
                commbank.data['AccountGroups'][0]['ListAccount'][-2]['AvailableFunds']
            )
            debit = commbank.get_currency(
                commbank.data['AccountGroups'][0]['ListAccount'][0]['AvailableFunds']
            )
            text = "%sC|%sD" % (credit, debit)
            log.warning("BankBalance:%s", text)
        except Exception as e:
            log.exception("BankBalance: %s %s", user, data)
        # text = commbank.net_position
        return str(text)

    def button_press(self, x, y, button):
        user = subprocess.check_output(
            ['python', expanduser("~/.bin/bank.py")]).strip().decode('utf8')
