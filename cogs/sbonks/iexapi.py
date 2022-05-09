from calendar import week
import os

import aiohttp
from cogs.sbonks.symboldata import SymbolData


class IEXAPIError(Exception):
    pass


class IEXAPI:
    KEY = os.getenv("IEXCLOUD_KEY")
    BASE_URL = "https://cloud.iexapis.com/stable"

    async def get_credits(self) -> int:
        params = {"token": self.KEY}
        url = f"{self.BASE_URL}/account/usage/credits"

        data = await self._get(url, params)
        return data.get("monthlyUsage", -1)

    async def get_quote(self, symbol: str) -> dict:
        params = {"token": self.KEY}
        url = f"{self.BASE_URL}/stock/{symbol}/quote"

        data = await self._get(url, params)
        return data

    async def get_intraday(self, symbols: list[str]) -> list[SymbolData]:
        """Request data for a single day for multiple symbols."""
        url = f"{self.BASE_URL}/stock/market/batch"
        params = {
            "types": "quote,intraday-prices",
            "symbols": ','.join(symbols),
            "displayPercent": "true"
        }

        iex_response = await self._get(url=url, params=params)

        data = []
        for symbol in symbols:

            if symbol not in iex_response.keys():
                continue

            quote = iex_response[symbol]["quote"]
            intraday = iex_response[symbol]["intraday-prices"]

            symbol_data = SymbolData(
                symbol=symbol,
                previous_close=quote["previousClose"],
                price=quote["latestPrice"],
                change=quote['change'],
                change_percent=quote["changePercent"],
                extended_price=quote.get("extendedPrice"),
                datapoints=[x['close'] for x in intraday]
            )
            data.append(symbol_data)

        return data

    async def get_week(self, symbol: str) -> SymbolData:
        return await self._get_chart(symbol, "5dm", 10)

    async def get_month(self, symbol: str) -> SymbolData:
        return await self._get_chart(symbol, "1m")

    async def get_three_month(self, symbol: str) -> SymbolData:
        return await self._get_chart(symbol, "3m", 2)

    async def get_six_month(self, symbol: str) -> SymbolData:
        return await self._get_chart(symbol, "6m", 4)

    async def get_year(self, symbol: str) -> SymbolData:
        return await self._get_chart(symbol, "1y", 6)

    async def get_two_year(self, symbol: str) -> SymbolData:
        return await self._get_chart(symbol, "2y", 8)

    async def get_five_year(self, symbol: str) -> SymbolData:
        return await self._get_chart(symbol, "5y", 20)

    async def get_max(self, symbol: str) -> SymbolData:
        return await self._get_chart(symbol, "max", 35)

    async def _get_chart(self, symbol: str, timeframe: str, interval: int = 1) -> SymbolData:
        url = f"{self.BASE_URL}/stock/{symbol}/chart/{timeframe}"
        params = {
            "chartCloseOnly": "true",
            "chartInterval": interval,
            "includeToday": "true"
        }

        data = await self._get(url=url, params=params)
        quote = await self.get_quote(symbol)

        change = quote["latestPrice"] - data[0]["close"]
        change_percent = abs(change) / data[0]["close"] * 100

        return SymbolData(
            symbol=quote["symbol"],
            previous_close=data[0]["close"],
            price=quote["latestPrice"],
            change=change,
            change_percent=change_percent,
            extended_price=quote.get("extendedPrice"),
            datapoints=[x['close'] for x in data],
            datalength=len(data),
            timeframe=timeframe.upper()
        )

    async def _get(self, url: str, params: dict | None = None) -> dict:
        """Underlying generic async api get request"""

        params = {} if params == None else params
        params.update({"token": self.KEY})

        # Make web request asynchronously
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    return await resp.json()
                raise IEXAPIError(f"IEX request failed: {resp.status}")
