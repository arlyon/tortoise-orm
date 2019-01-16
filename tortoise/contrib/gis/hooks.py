from collections import defaultdict
from typing import Dict

from pypika.queries import QueryBuilder

from pypika import Query

from tortoise import Model
from tortoise.backends.engines.base.client import emitter as client_emitter
from tortoise.backends.engines.base.schema_generator import emitter as schema_emitter
from tortoise.backends.engines.base.executor import emitter as executor_emitter
from tortoise.events import TableGenerationEvents, ConnectionEvents, ExecutorEvents
from tortoise.events.decorators import handles_event
from tortoise.function import func
from tortoise.contrib.gis.gis_fields import GeometryField

stripped_fields: Dict[Model, Dict[str, GeometryField]] = defaultdict(dict)


@handles_event(schema_emitter, TableGenerationEvents.before_generate_sql)
def remove_gis_from_creation(for_model):
    """Strips any instance of GeometryField out of the fields_db_projection during creation."""
    new_fields_db_projection = {}
    for k, v in for_model._meta.fields_db_projection.items():
        field_type = for_model._meta.fields_map[k]
        if isinstance(field_type, GeometryField):
            stripped_fields[for_model][k] = field_type
        else:
            new_fields_db_projection[k] = v

    for_model._meta.fields_db_projection = new_fields_db_projection


@handles_event(schema_emitter, TableGenerationEvents.after_generate_sql)
def inject_gis_field_creation_into_sql(table_data):
    """
    Insert the correct creation SQL into the final table schema,
    and re-insert the stripped fields into the fields_db_projection.
    """
    if table_data["model"] in stripped_fields:
        for field_name, field_type in stripped_fields[table_data["model"]].items():
            geometry_column_sql = f"{Query.select(func.AddGeometryColumn(table_data['table'], field_name, field_type.srid, field_type.geometry_type.value))};"
            table_data["table_creation_string"] += geometry_column_sql

        for k, v in stripped_fields[table_data["model"]].items():
            table_data["model"]._meta.fields_db_projection[k] = v.model_field_name


@handles_event(client_emitter, ConnectionEvents.connected)
async def register_spatialite_extension(connection):
    """Register the spatialite extension."""
    await connection.enable_load_extension(True)
    await connection.execute("SELECT load_extension('mod_spatialite');")
    await connection.execute("SELECT InitSpatialMetaData();")
    pass

