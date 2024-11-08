from dataclasses import dataclass

import yfinance as yf

from cogs.sbonks.symboldata import SymbolData

@dataclass
class YahooFinance:
    def get_quote(self, symbol: str) -> dict:
        """Return simple current data about a single ticker"""
        ticker = yf.Ticker(symbol)
        return ticker.info

    def get_history(self, symbol: str):
        ticker = yf.Ticker(symbol)
        return ticker.history(period="1d")

    def get_year(self, symbol: str) -> SymbolData:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1y", repair=True)

        print(data)

        # return SymbolData(symbol=symbol, price=ticker.info)
