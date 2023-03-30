import discord

NOTHING_PLAYING = discord.Embed(
    title="Nothing playing"
).add_field(
    name="Button Guide",
    value=(
        "🪙   Insert a coin to play a song\n\n"
        "🔁   Cycle between no repeat, repeat, and repeat one\n\n"
        "⏪ ⏩   Rewind/Skip (Rewind only restarts the song)\n\n"
        "🖼️   Toggle between the cover art and the queue\n\n"
        "🗑️   Clear the jukebox history\n\n"
        "♾️   Continue playing similar music after last song\n\n"
        "\u25C0 \u25B6 Next/Previous page in queue"
    )
)
