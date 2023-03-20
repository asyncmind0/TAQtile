from libqtile import widget
import requests


def get_exchange_rate(from_currency, to_currency):
    url = f"https://min-api.cryptocompare.com/data/price?fsym={from_currency}&tsyms={to_currency}"
    response = requests.get(url)
    exchange_rate = response.json()[to_currency]
    return exchange_rate


def convert_currency(amount, from_currency, to_currency):
    exchange_rate = get_exchange_rate(from_currency, to_currency)
    converted_amount = amount * exchange_rate
    return converted_amount


class ExchangeRate(widget.TextBox):
    def __init__(
        self, from_currency, to_currency, update_interval=60, **config
    ):
        self.from_currency = from_currency
        self.to_currency = to_currency

        self.update_interval = update_interval
        super().__init__(
            text=f"1 {self.from_currency} = {get_exchange_rate(self.from_currency, self.to_currency)} {self.to_currency}",
            **config,
        )

    def tick(self):
        self.text = f"1 {self.from_currency} = {get_exchange_rate(self.from_currency, self.to_currency)} {self.to_currency}"
        self.update(self.text)
