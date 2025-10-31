from typing import Optional, Callable, TypeVar
from sqlalchemy import select, func, Select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from ..middlewares import request_object
from ..schemas import PaginatedResponse

T_SQL = TypeVar('T_SQL')
T_Schema = TypeVar('T_Schema')

class Paginator:
    def __init__(self, session: AsyncSession, query: Select, page: int, per_page: int):
        self.session = session
        self.query = query
        self.page = page
        self.per_page = per_page
        self.limit = per_page
        self.offset = (page - 1) * per_page
        self.request = request_object.get()
        # computed later
        self.number_of_pages = 0
        self.next_page = ''
        self.previous_page = ''

    def _get_next_page(self) -> Optional[str]:
        if self.page >= self.number_of_pages:
            return None
        url = self.request.url.include_query_params(page=self.page + 1)
        return str(url)

    def _get_previous_page(self) -> Optional[str]:
        if self.page == 1 or self.page > self.number_of_pages + 1:
            return None
        url = self.request.url.include_query_params(page=self.page - 1)
        return str(url)

    def _get_number_of_pages(self, count: int) -> int:
        rest = count % self.per_page
        quotient = count // self.per_page
        return quotient if not rest else quotient + 1

    async def _get_total_count(self) -> int:
        count = await self.session.scalar(select(func.count()).select_from(self.query.subquery()))
        self.number_of_pages = self._get_number_of_pages(count)
        return count

    async def get_response(
            self,
            builder: Callable[[T_SQL, Request], T_Schema]
    ) -> PaginatedResponse[T_Schema]:

        count = await self._get_total_count()
        next_page_url = self._get_next_page()
        prev_page_url = self._get_previous_page()

        paginated_query = self.query.limit(self.limit).offset(self.offset)
        db_items = await self.session.scalars(paginated_query)

        items_with_links = [
            builder(item, self.request) for item in db_items
        ]

        return PaginatedResponse[T_Schema](
            count=count,
            next_page=next_page_url,
            previous_page=prev_page_url,
            items=items_with_links
        )


async def paginate(
        query: Select,
        page: int,
        per_page: int,
        session: AsyncSession,
        builder: Callable
) -> PaginatedResponse:
    paginator = Paginator(session, query, page, per_page)
    return await paginator.get_response(builder=builder)