from typing import Protocol, List, TYPE_CHECKING
from typing_extensions import runtime_checkable
if TYPE_CHECKING:
    from claire.claire_query import ClaireQuery
    from claire.claire_listing import ClaireListing

@runtime_checkable
class Searchable(Protocol):

    def search(self, query: 'ClaireQuery') -> List['ClaireListing']:
        pass


