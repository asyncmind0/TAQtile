from os.path import expanduser
import subprocess

try:
    from builtins import str
except Exception as e:
    from future.builtins import str

from libqtile.widget import base
from taqtile.log import logger

from .bank import CommBank


class BankBalance(base.ThreadedPollText):
    defaults = [
        ("warning", 300, "Warning limit."),
        ("warning_foreground", "#FF0000", "Warning Color - no updates."),
        ("warning_background", "", "Warning Color - no updates."),
        ("critical", 100, "Critical limit."),
        ("critical_foreground", "#FF0000", "Warning Color - no updates."),
        ("critical_background", "#FFffff", "Critical Color - no updates."),
        ("unavailable", "#ffffff", "Unavailable Color - no updates."),
        ("account", "debit", "Which account to show (all/0/1/2/...)"),
    ]
    fixed_upper_bound = False
    amount = None
    CACHE = {}

    def __init__(self, **config):
        # graph._Graph.__init__(self, **config)
        base.ThreadedPollText.__init__(self, **config)
        self.add_defaults(BankBalance.defaults)
        try:
            user = (
                subprocess.check_output(
                    ["pass", "financial/commbank/debit/user"]
                )
                .strip()
                .decode("utf8")
            )
            if not user:
                return
            password = (
                subprocess.check_output(
                    ["pass", "financial/commbank/debit/pass"],
                )
                .strip()
                .decode("utf8")
            )
            self.commbank = CommBank(user, password)
        except:
            logger.exception("Failed to get pasword")

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
            logger.exception("Draw error")
        except Exception as e:
            logger.exception("Draw error")
        self.foreground = foreground
        self.background = background
        base.ThreadedPollText.draw(self)

    def poll(self, data=None):
        text = "$$$$"
        user = None
        if not self.commbank:
            return str(text)
        try:
            logger.warning("BankBalance:%s", user)
            self.commbank.update()
            self.data = data = self.commbank.data
            if self.account == "credit":
                self.amount = self.commbank.get_currency(
                    self.commbank.data["AccountGroups"][1]["ListAccount"][-2][
                        "AvailableFunds"
                    ]
                )
            else:
                self.amount = self.commbank.get_currency(
                    self.commbank.data["AccountGroups"][1]["ListAccount"][0][
                        "AvailableFunds"
                    ]
                )
            text = "%s%s" % (
                self.amount,
                "C" if self.account == "credit" else "D",
            )
            logger.warning("BankBalance:%s", text)
        except Exception as e:
            logger.exception("BankBalance: %s %s", user, data)
        # text = commbank.net_position
        return str(text)

    def button_press(self, x, y, button):
        subprocess.check_output(
            "notify-send %s"
            % str(
                subprocess.check_output(
                    [
                        "python",
                        expanduser("~/.bin/bank.py"),
                    ]
                )
                .strip()
                .decode("utf8")
            )
        )
