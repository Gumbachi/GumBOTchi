import io
import random
from dataclasses import dataclass
import discord
import matplotlib.font_manager as font_manager
import matplotlib.pyplot as plt
import numpy as np

# Load matplotlib font
for font in font_manager.findSystemFonts(["./src/res/fonts"]):
    font_manager.fontManager.addfont(path=font)


@dataclass(slots=True)
class SymbolData:
    """Class representing data for one symbol."""

    symbol: str
    price: float
    change: float
    change_percent: float
    extended_price: float | None
    datapoints: list[float]
    previous_close: float
    datalength: int = 390  # What is the max amount of data points
    timeframe: str = "1D"  # The timeframe label to use on the graph
    style: str = "src/cogs/sbonks/styles/sbonks.mplstyle"  # The mpl style file

    @staticmethod
    def mock(text: str) -> str:
        mocked = [random.choice((c.upper(), c.lower())) for c in text]
        return "".join(mocked)

    def get_interpolated_data(self, precision: int = 5) -> list[float]:
        """Fill in the gaps in the data with previous data found."""

        def find_last(i):
            for i in range(i, 0, -1):
                if self.datapoints[i]:
                    return self.datapoints[i]
            return self.datapoints[i] or self.previous_close

        interpolated = [find_last(i) for i in range(len(self.datapoints))]
        interpolated += [np.nan] * (self.datalength - len(interpolated))
        return interpolated[::precision]

    def graph(
        self, precision: int = 5, description: str | None = None, mock: bool = False
    ) -> discord.File:
        """Draw chart representing the symboldata"""
        arrow = "▲" if self.price >= self.previous_close else "▼"
        color = "lime" if self.price >= self.previous_close else "red"
        prices = self.get_interpolated_data(precision=precision)
        # plot graph
        plt.style.use(self.style)  # use defined style
        plt.clf()  # Reset so graphs dont overlap. This must be after plt.style.use
        plt.axis("off")  # disable labels maybe could move this to .mplstyle
        plt.xlim(0, len(prices))
        plt.plot(list(range(len(prices))), prices, color=color)
        plt.axhline(y=self.previous_close, color="grey", linestyle="dotted")
        ax = plt.gca()  # get current axes for transform
        # add Symbol and price text
        price = self.extended_price or self.price
        text = f"{self.symbol} ${price:.2f}"
        plt.text(
            x=0,
            y=1.1,
            s=text,
            va="bottom",
            ha="left",
            size=35,
            c="white",
            transform=ax.transAxes,
        )
        # add change text
        change_text = f"{arrow} {abs(self.change):.2f} ({self.change_percent:.2f}%)"
        plt.text(
            x=0,
            y=1,
            s=change_text,
            va="bottom",
            ha="left",
            size=25,
            c=color,
            transform=ax.transAxes,
        )
        # Draw timeframe text
        plt.text(
            x=1,
            y=1.15,
            s=self.timeframe,
            va="bottom",
            ha="right",
            size=20,
            c="gray",
            transform=ax.transAxes,
        )
        # Draw special message
        if description:
            message = description if not mock else self.mock(description)
            plt.text(
                x=0,
                y=0,
                s=message,
                va="top",
                ha="left",
                size=20,
                c="gray",
                transform=ax.transAxes,
            )
        # convert the chart to a discord.File
        buffer = io.BytesIO()
        plt.savefig(buffer)
        buffer = buffer.getvalue()
        return discord.File(fp=io.BytesIO(buffer), filename=f"{self.symbol}.png")
