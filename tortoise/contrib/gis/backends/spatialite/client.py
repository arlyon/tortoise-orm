from tortoise.backends.base.client import Capabilities
from tortoise.backends.sqlite import SqliteClient
from tortoise.contrib.gis.backends.spatialite.schema_generator import SpatialiteSchemaGenerator


class SpatialiteClient(SqliteClient):
    schema_generator = SpatialiteSchemaGenerator

    def __init__(self, file_path, *args, **kwargs):
        super().__init__(file_path, *args, **kwargs)
        self.capabilities = Capabilities(
            'spatialite',
            connection={'file': file_path},
            safe_indexes=True,
        )

    async def create_connection(self, with_db: bool):
        await super().create_connection(with_db)
        await self._connection.enable_load_extension(True)
        await self._connection.execute("SELECT load_extension('mod_spatialite');")
        await self._connection.execute("SELECT InitSpatialMetaData();")
