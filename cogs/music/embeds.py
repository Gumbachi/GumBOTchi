import discord

NOTHING_PLAYING = discord.Embed(
    title="Nothing playing"
).add_field(
    name="Button Guide",
    value="""
        🪙   Insert a coin to play a song\n
        🔁   Cycle between no repeat, repeat, and repeat one\n
        ⏪ ⏩   Rewind/Skip (Rewind only restarts the song)\n
        🖼️   Toggle between the cover art and the queue\n
        🗑️   Clear the jukebox history\n
        ♾️   Continue playing similar music after last song\n
        \u25C0 \u25B6 Next/Previous page in queue
    """
)
