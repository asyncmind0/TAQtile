import subprocess

from libqtile.widget import base

from bank import CommBank


class BankBalance(base.ThreadedPollText):
    defaults = [
        ('warning', 300, 'Warning limit.'),
        ('warning_foreground', 'FF0000', 'Warning Color - no updates.'),
        ('warning_background', '', 'Warning Color - no updates.'),
        ('critical', 100, 'Critical limit.'),
        ('critical_foreground', 'FF0000', 'Warning Color - no updates.'),
        ('critical_background', 'FFffff', 'Critical Color - no updates.'),
        ('unavailable', 'ffffff', 'Unavailable Color - no updates.'),
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
                foreground = self.warning
            elif float(self.text) <= self.critical:
                background = self.critical_background
                foreground = self.critical
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
                ['pass', "financial/commbank/debit/user"]).strip()
            password = subprocess.check_output(
                ['pass', "financial/commbank/debit/pass"]).strip()
            log.warning("BankBalance:%s", user)
            commbank = CommBank(user, password)
            self.data = data = commbank.data
            text = commbank.get_currency(
                commbank.data['AccountGroups'][0]['ListAccount'][-2]['AvailableFunds']
            )
            log.warning("BankBalance:%s", text)
        except Exception as e:
            log.exception("BankBalance: %s %s", user, data)
        # text = commbank.net_position
        return str(text)

