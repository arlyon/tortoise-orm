from collections import defaultdict
from typing import Dict

from pypika import Query

from tortoise import Model
from tortoise.backends.sqlite.schema_generator import SqliteSchemaGenerator
from tortoise.contrib.gis import gis_fields
from tortoise.contrib.gis.gis_fields import GeometryField
from tortoise.function import func


class SpatialiteSchemaGenerator(SqliteSchemaGenerator):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.FIELD_TYPE_MAP.update({
            gis_fields.GeometryField: '__GEOMETRY',  # this is stripped out
        })
        self.stripped_fields: Dict[Model, Dict[str, GeometryField]] = defaultdict(dict)

    def _before_generate_sql(self, model):
        new_fields_db_projection = {}
        for k, v in model._meta.fields_db_projection.items():
            field_type = model._meta.fields_map[k]
            if isinstance(field_type, GeometryField):
                self.stripped_fields[model][k] = field_type
            else:
                new_fields_db_projection[k] = v

        model._meta.fields_db_projection = new_fields_db_projection

    def _after_generate_sql(self, table_data):
        if table_data["model"] in self.stripped_fields:
            for field_name, field_type in self.stripped_fields[table_data["model"]].items():
                geometry_column_sql = str(Query.select(
                    func.AddGeometryColumn(
                        table_data['table'], field_name, field_type.srid,
                        field_type.geometry_type.value
                    )
                ))
                table_data["table_creation_string"] += f"{geometry_column_sql};"

            for k, v in self.stripped_fields[table_data["model"]].items():
                table_data["model"]._meta.fields_db_projection[k] = v.model_field_name
