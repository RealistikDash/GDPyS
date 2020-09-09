from objects.levels import SearchQuery
from conn.mysql import myconn
from helpers.generalhelper import safe_id_list, create_offsets_from_page
from helpers.userhelper import user_helper
from dataclasses import dataclass

@dataclass # I probably should put this into objects but it isnt used anywhere else so i will place it here
class QueryResponse():
    """Small object responsible for storing 2 data values returned by your search."""
    total_results : int
    results : list

class BasicMysqlSearch():
    """A simple search element."""
    def __init__(self):
        """Inits the search element."""
        # I may add caches but meh
        pass

    async def get_levels(self, filters : SearchQuery):
        """Searches levels and returns list of IDs."""

        # Constructing the SQL query.
        pass # Lol levels arent done yet lmfao

    async def get_accounts_search(self, search_query : str, page : int) -> QueryResponse:
        """Returns list of ids that match search query."""
        search_query = f"%{search_query}%" # For the like statement
        offset = create_offsets_from_page(int(page))
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute("SELECT accountID FROM accounts WHERE userName LIKE %s LIMIT 10 OFFSET %s", (search_query, offset))
            db_retults = await mycursor.fetchall()
            # Simple count query. I'm not sure how else to do it other than yet another query :(
            await mycursor.execute("SELECT COUNT(*) FROM accounts WHERE userName LIKE %s", (search_query,))
            count = await mycursor.fetchone()
        results = [i[0] for i in db_retults]
        return QueryResponse(count[0], results)


class SearchQueryFormatter():
    """Provides a nice API for interpreting search query responses."""
    def __init__(self):
        self.search_engine : BasicMysqlSearch = BasicMysqlSearch() # If you make your own one thats GDPyS compatible (or make a wrapper), just change the class here and all will work.
    
    async def get_users(self, query : str, page : int) -> QueryResponse:
        """Returns list of user objects that watch search query."""
        accs = await self.search_engine.get_accounts_search(query, page)
        return QueryResponse(accs.total_results, [await user_helper.get_object(i) for i in accs.results]) # Oh i love this

search_helper = SearchQueryFormatter()
