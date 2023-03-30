from enum import Enum
from .craigslist import Craigslist
from .searchable import Searchable

class Sources(Enum):
    CRAIGSLIST=Craigslist
    OFFERUP="Offer-up"

    def is_valid(self) -> bool:
        return isinstance(self.value, Searchable)
    
    @classmethod
    def get_name(cls, src: object) -> str:
        for source in cls:
            if source.value == src:
                return source.name