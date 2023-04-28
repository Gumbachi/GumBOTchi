from enum import Enum

from cogs.claire.api.modules.craigslist import Craigslist
from cogs.claire.api.modules.offerup import OfferUp
from cogs.claire.api.modules.searchable import Searchable


class Sources(Enum):
    CRAIGSLIST=Craigslist
    OFFERUP=OfferUp

    def is_valid(self) -> bool:
        return isinstance(self.value, Searchable)
    
    @classmethod
    def get_name(cls, src: object) -> str:
        for source in cls:
            if source.value == src:
                return source.name