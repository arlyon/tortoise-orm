from typing import Optional

from tortoise.fields import Field
from tortoise.function import Function


class GeomFromText(Function):
    """Generates geometry from well known text."""

    def __init__(self, wkt: str, srid: Optional[int] = None, alias=None):
        """
        Generate geometry from the given well-known text.
        :param wkt: The well-known text to insert.
        :param srid: The (optional) SRID to interpret it as..
        :param alias: The alias for the function.
        """
        args = filter(lambda x: x is not None, (wkt, srid))
        super().__init__("GeomFromText", *args, alias=alias)


class AsWKT(Function):
    def __init__(self, field: Field, alias=None):
        super().__init__("AsWKT", field, alias=alias)
