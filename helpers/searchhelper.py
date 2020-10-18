# This will probably be rewritten either way soon
from objects.levels import SearchQuery, Level
from objects.misc import QueryResponse
from conn.mysql import myconn
from helpers.generalhelper import safe_id_list, create_offsets_from_page, SelectQueryBuilder
from helpers.userhelper import user_helper
from helpers.levelhelper import level_helper
from helpers.timehelper import week_ago


class BasicMysqlSearch():
    """A simple search element."""

    def __init__(self):
        """Inits the search element."""
        pass

    async def get_levels(self, filters: SearchQuery):
        """Searches levels and returns list of IDs."""
        query = SelectQueryBuilder("levels")
        query.limit = 10
        query.offset = filters.offset
        query.set_order("uploadDate")
        query.select_add("levelID")

        # I hate working with the filters... It looks ugly and this is one of the most called functions...
        if filters.search_type in (0, 15):
            if filters.search_query.isnumeric:
                # level ID search
                query.where_equals("levelID", filters.search_query)
            else:
                query.where_like_token("levelName", filters.search_query)
        elif filters.search_type == 1:
            query.set_order("downloads")
        elif filters.search_type == 2:
            query.set_order("likes")
        elif filters.search_type == 3:
            # format safe since we trust it
            query.where_more_than("uploadDate", week_ago(), True)
        elif filters.search_type == 4:
            pass
        elif filters.search_type == 5:
            query.where_equals("userID", filters.search_query)
            query.set_order("uploadDate DESC")
        elif filters.search_type == 6:
            query.where_equals("starFeatured", 1)
        elif filters.search_type == 7:
            query.where_equals("magic", 1)
        elif filters.search_type == 10:
            query.where_in_int_list("levelID", filters.search_query)
        elif filters.search_type == 11:
            query.where_equals("awarded", 1)
        # TODO : 12 = followed, 13 = friends
        elif filters.search_type == 16:
            query.where_equals("starEpic", 1)

        # now we do the other sub

        # TODO: all the other mini filters, this is more of proof of concept or proof it works at all
        async with myconn.conn.cursor() as mycursor:
            query_exec, args = query.build()
            await mycursor.execute(query_exec, args)
            plays = await mycursor.fetchall()
            count_query, count_args = query.build_count()
            await mycursor.execute(count_query, count_args)
            count = (await mycursor.fetchone())[0]
        return QueryResponse(count, [i[0] for i in plays])

    async def get_accounts_search(self, search_query: str, page: int) -> QueryResponse:
        """Returns list of ids that match search query."""
        search_query = f"%{search_query}%"  # For the like statement
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
        # If you make your own one thats GDPyS compatible (or make a wrapper), just change the class here and all will work.
        self.search_engine: BasicMysqlSearch = BasicMysqlSearch()

    async def get_users(self, query: str, page: int) -> QueryResponse:
        """Returns list of user objects that watch search query."""
        accs = await self.search_engine.get_accounts_search(query, page)
        # Oh i love this
        return QueryResponse(accs.total_results, [await user_helper.get_object(i) for i in accs.results])

    async def get_levels(self, search_filters: SearchQuery) -> QueryResponse:
        """Returns a list of level objects."""
        levels = await self.search_engine.get_levels(search_filters)
        return QueryResponse(
            levels.total_results,
            await level_helper.level_list_objs(levels.results)
        )


search_helper = SearchQueryFormatter()
