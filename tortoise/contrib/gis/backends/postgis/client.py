from typing import SupportsInt

from asyncpg import DuplicateObjectError

from tortoise.backends.asyncpg import AsyncpgDBClient
from tortoise.backends.base.client import Capabilities
from tortoise.contrib.gis.backends.postgis.schema_generator import PostGISSchemaGenerator


class PostGISClient(AsyncpgDBClient):
    schema_generator = PostGISSchemaGenerator

    def __init__(
            self, user: str, password: str, database: str, host: str, port: SupportsInt, **kwargs
    ):
        super().__init__(user, password, database, host, port, **kwargs)
        self.capabilities = Capabilities('postgis', safe_indexes=True)

    async def create_connection(self, with_db: bool):
        await super().create_connection(with_db)
        try:
            await self._connection.execute("CREATE EXTENSION postgis;")
        except DuplicateObjectError:
            # extension loaded
            pass
