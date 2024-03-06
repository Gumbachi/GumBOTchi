import io
from typing import List
from datetime import datetime, timedelta
import discord

import matplotlib.pyplot as plt
import pandas as pd

from .time_series import ChartLength, TimeSeriesData

plt.style.use("./styles/sbonks.mplstyle")

def display(
    name: str,
    time_series_data: List[TimeSeriesData],
    length: ChartLength,
):
    """Graphs specified ticker from the data available in the Database"""

    start = datetime.now()
    end = start - timedelta(days=length)

    df = pd.DataFrame(time_series_data)
    df.type = df.type.astype(str)

    # Filter only relevant data and sort by date
    df = df.query(
        "type==@kind.value and (@start <= date <= @end)") \
        .sort_values(
            by='date',
            ascending=False
        )

    # If there is no data leave
    if len(df) == 0:
        print(f"No data for found for {name} between {start} and {end}")
        return

    # Assigns color values depending on whether the
    # closing price was higher or lower than the open price
    df['color'] = df.apply(lambda row: 'green' if (
        row.close - row.open) > 0 else 'darkred', axis=1)

    last = df.iloc[0]
    first = df.iloc[-1]

    change = abs(last.close - first.close)
    pct_change = (last.close / first.close) * 100

    arrow = "▲" if last.close >= first.close else "▼"
    color = "lime" if last.close >= first.close else "red"

    figure = plt.figure()
    figure.set_figwidth(15)
    figure.set_figheight(5)

    ax1 = figure.add_subplot(111, label='outliers', frame_on=False)
    ax2 = figure.add_subplot(111, label='vol', frame_on=False)
    ax3 = figure.add_subplot(111, label='price', frame_on=False)

    # Setting the X and x limits since theyre the same
    X = df.date

    # Set graph limits
    ax1.set_xlim(first.date, last.date)
    ax2.set_xlim(first.date, last.date)
    ax3.set_xlim(first.date, last.date)

    ax1.set_ylim(df.close.min(), df.close.max())
    ax2.set_ylim(0, df.volume.max()*2)
    ax3.set_ylim(df.close.min(), df.close.max())

    # Remove all ticks
    ax1.xaxis.set_ticks([])
    ax1.yaxis.set_ticks([])
    ax2.xaxis.set_ticks([])
    ax2.yaxis.set_ticks([])

    # Current price
    ax3.axhline(y=last.close, color="gray", linestyle="dotted")

    # Title annotation
    price = last.close

    text = f"{name}\n${price:.2f}"
    ax3.text(x=0, y=1.1, s=text, va="bottom", ha="left",
            size=35, c="white", transform=ax3.transAxes)
    ax3.tick_params(axis='x', colors="white")
    ax3.tick_params(axis='y', colors="white")

    # Change annotation
    change_text = f"{arrow} {change:.2f} ({pct_change:.2f}%)"
    ax3.text(x=0, y=1, s=change_text, va="bottom", ha="left",
            size=25, c=color, transform=ax3.transAxes)

    # Date annotation
    date_range = f'{first.date} to {last.date}'.replace('-', '/')
    ax3.set_xlabel(date_range, color="white")

    ax2.bar(X, df.volume, color=df.color, alpha=0.7)
    ax3.plot(X, df.close, color=color)

    buffer = io.BytesIO()
    plt.savefig(buffer)
    buffer = buffer.getvalue()
    return discord.File(
        fp=io.BytesIO(buffer),
        filename=f"{name}.png"
    )