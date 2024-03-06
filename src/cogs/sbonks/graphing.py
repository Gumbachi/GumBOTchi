import io
from typing import List
from datetime import datetime, timedelta
import discord

import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import pandas as pd

from .time_series import ChartLength, TimeSeriesData

plt.style.use("src/cogs/sbonks/styles/sbonks.mplstyle")

def display(
    name: str,
    time_series_data: List[TimeSeriesData],
    length: ChartLength,
):
    """Graphs specified ticker from the data available in the Database"""

    end = datetime.now()
    start = end - timedelta(days=length.value)

    df = pd.DataFrame(time_series_data)
    df.type = df.type.astype(str)

    # Filter only relevant data and sort by date
    df = df.query(
        "@start <= date <= @end") \
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
    pct_change = (last.close / first.close - 1) * 100

    arrow = "▲" if last.close >= first.close else "▼"
    color = "lime" if last.close >= first.close else "red"

    figure = plt.figure()
    figure.set_figwidth(15)
    figure.set_figheight(5)

    ax = figure.add_subplot(111, label='price', frame_on=False)

    # Setting the X and x limits since theyre the same
    X = df.date

    # Set graph limits
    ax.set_xlim(first.date, last.date)

    ax.set_ylim(df.close.min(), df.close.max())

    # Current price
    ax.axhline(y=last.close, color="gray", linestyle="dotted")

    # Title annotation
    price = last.close

    text = f"{name}\n${price:.2f}"
    ax.text(x=0, y=1.1, s=text, va="bottom", ha="left",
            size=35, c="white", transform=ax.transAxes)
    ax.tick_params(axis='x', colors="white")
    ax.tick_params(axis='y', colors="white")

    # Change annotation
    change_text = f"{arrow} {change:.2f} ({pct_change:.2f}%)"
    ax.text(x=0, y=1, s=change_text, va="bottom", ha="left",
            size=25, c=color, transform=ax.transAxes)

    # Date annotation
    date_range = f'{first.date} to {last.date}'.replace('-', '/')
    ax.set_xlabel(date_range, color="white")

    # Fix X Axis ticks
    date_format = DateFormatter("%d/%m %#I:%M%p")
    if (first.date.date() == last.date.date()):
        date_format = DateFormatter("%#I:%M%p")
    ax.xaxis.set_major_formatter(date_format)

    ax.plot(X, df.close, color=color)

    buffer = io.BytesIO()
    plt.savefig(buffer)
    buffer = buffer.getvalue()
    
    return discord.File(
        fp=io.BytesIO(buffer),
        filename=f"{name}.png"
    )