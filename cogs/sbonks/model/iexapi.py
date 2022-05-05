import os

import aiohttp
from cogs.sbonks.model.symboldata import SymbolData


class IEXAPIError(Exception):
    pass


class IEXAPI:
    KEY = os.getenv("IEXCLOUD_KEY")
    BASE_URL = "https://cloud.iexapis.com/stable"

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

    async def get_week(self, symbols: list[str]) -> list[SymbolData]:
        return []

    async def get_year(self, symbols: list[str]) -> list[SymbolData]:
        return []

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
