import aiohttp
import asyncio
from dataclasses import dataclass
import json

@dataclass
class TickerInfo:
    last: float  # Last price
    baseVolume: float  # Base currency volume_24h
    quoteVolume: float  # Target currency volume_24h
    
    def __dict__(self):
        return {
            "last": self.last,
            "baseVolume": self.baseVolume,
            "quoteVolume": self.quoteVolume,
        }

Symbol = str  # Trading pair like ETH/USDT


class BaseExchange:
    async def fetch_data(self, url: str):
        """
        :param url: URL to fetch the data from exchange
        :return: raw data
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp and resp.status == 200:
                    data = await resp.json()
                else:
                    raise Exception(resp)
        return data

    async def fetch_tickers(self) -> dict[Symbol, TickerInfo]:
        """
            Method fetch data from exchange and return all tickers in normalized format
            :return:
        """
        raise NotImplementedError


    def normalize_data(self, data: dict) -> dict[Symbol, TickerInfo]:
        """
            :param data: raw data received from the exchange
            :return: normalized data in a common format
        """
        raise NotImplementedError

    def _convert_symbol_to_ccxt(self, symbols: str) -> Symbol:
        """
            Trading pairs from the exchange can come in various formats like: btc_usdt, BTCUSDT, etc.
            Here we convert them to a value like: BTC/USDT.
            The format is as follows: separator "/" and all characters in uppercase
            :param symbols: Trading pair ex.: BTC_USDT
            :return: BTC/USDT
        """
        raise NotImplementedError

    async def load_markets(self):
        """
            Sometimes the exchange does not have a route to receive all the tickers at once.
            In this case, you first need to get a list of all trading pairs and save them to self.markets.(Ex.2)
            And then get all these tickers one at a time.
            Allow for delays between requests so as not to exceed the limits
            (you can find the limits in the documentation for the exchange API)
        """

    async def close(self):
        pass  # stub, not really needed



class CoinGeckoExchange(BaseExchange):
    BASE_URL = "https://api.coingecko.com/api/v3/"

    async def fetch_tickers(self) -> dict[Symbol, TickerInfo]:
        url = self.BASE_URL + "coins/markets?vs_currency=usd"
        data = await self.fetch_data(url)
        return self.normalize_data(data)

    def normalize_data(self, data: dict) -> dict[Symbol, TickerInfo]:
        normalized_data = {}
        for item in data:
            symbol = self._convert_symbol_to_ccxt(item["symbol"].upper())
            last = item["current_price"]
            baseVolume = item["total_volume"]
            quoteVolume = item["market_cap"]
            normalized_data[symbol] = TickerInfo(last, baseVolume, quoteVolume).__dict__()
        return normalized_data

    def _convert_symbol_to_ccxt(self, symbol: str) -> Symbol:
        return symbol.upper() + "/USD"

async def main():
    exchange = CoinGeckoExchange()
    tickers = await exchange.fetch_tickers()
    print(json.dumps(tickers, indent=1))

asyncio.run(main())
