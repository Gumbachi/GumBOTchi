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
        url = f"{self.BASE_URL}/stock/{symbol}/chart/5dm"
        params = {
            "chartCloseOnly": "true",
            "chartInterval": "10",
            "includeToday": "true"
        }
        week_data = await self._get(url=url, params=params)
        quote = await self.get_quote(symbol)

        print(week_data)

        change = quote["latestPrice"] - week_data[0]["open"]
        change_percent = abs(change) / week_data[0]["open"] * 100

        return SymbolData(
            symbol=quote["symbol"],
            previous_close=week_data[0]["open"],
            price=quote["latestPrice"],
            change=change,
            change_percent=change_percent,
            extended_price=quote.get("extendedPrice"),
            datapoints=[x['close'] for x in week_data],
            datalength=len(week_data)
        )

    async def get_year(self, symbol: str) -> SymbolData:
        pass

    async def _get(self, url: str, params: dict | None = None) -> dict:
        """Underlying api request function."""

        params = {} if params == None else params
        params.update({"token": self.KEY})

        # Make web request asynchronously
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    return await resp.json()
                raise IEXAPIError(f"IEX request failed: {resp.status}")
