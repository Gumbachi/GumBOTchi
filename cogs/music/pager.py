from dataclasses import dataclass
from typing import Any

from common.utils import chunk


@dataclass
class Pager:
    page: int = 1
    page_size: int = 3

    def total_pages(self, songlist: list[Any]):
        amount = len(chunk(songlist, self.page_size))
        return 1 if amount == 0 else amount
