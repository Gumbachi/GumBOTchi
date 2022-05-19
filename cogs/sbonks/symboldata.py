import io
import numpy as np
import random
import matplotlib.pyplot as plt
import discord


class SymbolData:
    """Class representing data for one symbol."""

    def __init__(
        self,
        symbol: str,
        price: float,
        change: float,
        change_percent: float,
        extended_price: float | None,
        datapoints: list[float],
        previous_close: float | None = None,
        datalength: int = 390,  # What is the max amount of data points
        timeframe: str = "1D",
        style: str = "./cogs/sbonks/styles/sbonks.mplstyle"  # The mpl style file
    ) -> None:
        self.symbol = symbol
        self.previous_close = previous_close
        self.price = price
        self.change = change
        self.change_percent = change_percent
        self.extended_price = extended_price
        self.datapoints = datapoints
        self.datalength = datalength
        self.timeframe = timeframe
        self.style = style

    @property
    def color(self):
        """What color the graph should be based on prices."""
        return "lime" if self.price >= self.previous_close else "red"

    @property
    def arrow(self):
        "UP/DOWN arrow determining if mooning or sinking"
        return "▲" if self.price >= self.previous_close else "▼"

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

    def graph(self, precision: int = 5, description: str | None = None) -> discord.File:
        """Draw chart representing the symboldata"""
        prices = self.get_interpolated_data(precision=precision)

        # plot graph
        plt.style.use(self.style)  # use defined style
        plt.clf()  # Reset so graphs dont overlap. This must be after plt.style.use
        plt.axis('off')  # disable labels maybe could move this to .mplstyle
        plt.xlim(0, len(prices))
        plt.plot(list(range(len(prices))), prices, color=self.color)
        plt.axhline(y=self.previous_close, color="grey", linestyle="dotted")
        ax = plt.gca()  # get current axes for transform

        # add Symbol and price text
        price = self.extended_price or self.price
        text = f"{self.symbol} ${price:.2f}"
        plt.text(x=0, y=1.1, s=text, va="bottom", ha="left",
                 size=35, c="white", transform=ax.transAxes)

        # add change text
        change_text = f"{self.arrow} {abs(self.change):.2f} ({self.change_percent:.2f}%)"
        plt.text(x=0, y=1, s=change_text, va="bottom", ha="left",
                 size=25, c=self.color, transform=ax.transAxes)

        # Draw timeframe text
        plt.text(x=1, y=1.15, s=self.timeframe, va="bottom", ha="right",
                 size=20, c="gray", transform=ax.transAxes)

        # Draw special message
        if description:
            plt.text(x=0, y=0, s=description, va="top", ha="left",
                     size=20, c="gray", transform=ax.transAxes)

        # convert the chart to a discord.File
        buffer = io.BytesIO()
        plt.savefig(buffer)
        buffer = buffer.getvalue()
        return discord.File(
            fp=io.BytesIO(buffer),
            filename=f"{self.symbol}.png"
        )


def mock(text):
    mocked_letters = [random.choice((c.upper(), c.lower())) for c in text]
    return "".join(mocked_letters)
