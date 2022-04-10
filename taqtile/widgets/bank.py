#!/usr/bin/python
# TODO docopts, qtile-widget
# TODO daily spending report
# TODO text console report

import json
import requests
import re
import os
import logging
from plumbum import local


# import paypalrestsdk
# class PayPal():
#    def __int__(self):
#        keepass_entry_path = 'Internet/paypal/api'
#        client_id = get_keepass_path(keepass_entry_path, 'UserName')
#        client_secret = get_keepass_path(keepass_entry_path, 'Password')
#        paypalrestsdk.configure({
#            "mode": "sandbox", # sandbox or live
#            "client_id": client_id,
#            "client_secret": client_secret})


class CommBank:
    loginUrl = "https://www2.my.commbank.com.au/mobile/t/ajaxcalls.aspx"
    total_credit = 1300.0
    regex_currency = re.compile(r"^\$(\d+(\.\d*)?|\.\d+)(.*)")

    def __init__(self, clientnumber, password):
        self.clientNumber = clientnumber
        self.password = password

    def update(self):
        postdata = {
            "Params": [
                {"Name": "Request", "Value": "login"},
                {"Name": "UserName", "Value": str(self.clientNumber)},
                {"Name": "Password", "Value": str(self.password)},
                {"Name": "Token", "Value": ""},
                {"Name": "AccountIds", "Value": "1,2,3,4,5,6"},
            ]
        }
        postdata = json.dumps(postdata)
        headers = {
            "content-type": "application/json",
            "content-length": len(postdata),
        }
        response = requests.post(self.loginUrl, data=postdata, headers=headers)
        try:
            self.data = json.loads(response.text[2:-2])
        except Exception as e:
            logging.exception("Error decoding : %s" % response.text)

    def get_currency(self, value):
        if not value:
            return 0
        amount, cents, crdr = self.regex_currency.match(
            value.replace(",", "")
        ).groups()
        crdr = crdr.strip()
        return float(amount) if crdr == "CR" else -1.0 * float(amount)

    @property
    def net_position(self):
        return self.get_currency(self.data["AccountGroups"][0]["NetPosition"])

    @property
    def total_credits(self):
        return self.get_currency(self.data["AccountGroups"][0]["TotalCredits"])


if __name__ == "__main__":
    unixpass = local["pass"]
    commbank = CommBank(
        unixpass("financial/commbank/debit/user").strip(),
        unixpass("financial/commbank/debit/pass").strip(),
    )
    accountgroup_format = (
        "TotalCredits: {TotalCredits}\n" "NetPosition: {NetPosition}"
    )
    account_format = "{AccountName}: " "{AvailableFunds}" "/{Balance}"
    # import ipdb; ipdb.set_trace()
    notifications = []
    for accountGroup in commbank.data["AccountGroups"]:
        notifications.append(accountgroup_format.format(**accountGroup))
        for account in accountGroup["ListAccount"]:
            if account["ProductTypeCode"] not in ["54", "04"]:
                continue
            account["AvailableFunds"] = commbank.get_currency(
                account["AvailableFunds"]
            )
            account["Balance"] = commbank.get_currency(account["Balance"])
            notifications.append(account_format.format(**account))
    notification = "\n".join(notifications)
    print(notification)
    notify_send = local["notify-send"]
    notify_send(notification)  # , _env=os.environ)
