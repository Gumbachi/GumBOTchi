from yt_dlp import YoutubeDL
from discord.ext.commands import UserInputError
import time

YDL_OPTS = {
    "format": "bestaudio/best",
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",  # bind to ipv4
}


class Song():
    """Represents song/youtube video metadata"""

    def __init__(self, **songdata) -> None:
        self.title = songdata['title']
        self._duration = songdata['duration']
        self.url = songdata['url']
        self.webpage_url = songdata['webpage_url']
        self.thumbnail = songdata['thumbnail']

    @property
    def embed_format(self):
        return f"[{self.title}]({self.webpage_url})\n{self.duration}"

    @property
    def duration(self) -> str:
        if self._duration < 3600:
            return time.strftime("%M:%S", time.gmtime(self._duration))
        return time.strftime("%H:%M:%S", time.gmtime(self._duration))

    @classmethod
    def from_query(cls, query: str):
        """Uses youtubeDL(ytdlp) to query song data."""
        with YoutubeDL(YDL_OPTS) as ydl:
            song_info = ydl.extract_info(f"ytsearch:{query}", download=False)

            # Couldn't find song
            if "entries" not in song_info:
                raise UserInputError("Song not found.")

            # filter out only useful details
            return cls(**song_info["entries"][0])
