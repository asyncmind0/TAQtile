from libqtile import widget
import requests


class ExchangeRate(widget.GenPollUrl):
    def __init__(self, from_currency, to_currency, **config):
        self.from_currency = from_currency
        self.to_currency = to_currency
        super().__init__(
            json=True,
            url=f"https://min-api.cryptocompare.com/data/price?fsym={from_currency}&tsyms={to_currency}",
            **config,
        )

    def parse(self, body):
        amount = 1
        return f"{amount} {self.from_currency} = {amount * body[self.to_currency]} {self.to_currency}"


class BitcoinFees(widget.GenPollUrl):
    def __init__(self, **config):
        super().__init__(
            json=True,
            url="https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_market_cap=false&include_24hr_vol=false&include_24hr_change=false&include_last_updated_at=false",
            **config,
        )

    def parse(self, body):
        btc_price_usd = body["bitcoin"]["usd"]

        # Assuming transaction fees are 0.5% of the Bitcoin price in USD
        transaction_fees = btc_price_usd * 0.005

        return f"fee: {transaction_fees}"
