from itertools import chain
from typing import Union, Optional

from pypika import Field as PyPikaField
from shapely.geometry.base import BaseGeometry
from shapely.wkt import dumps

from tortoise.contrib.gis.gis_functions import GeomFromText
from tortoise.fields import Field
from tortoise.function import Function

GeometryLike = Union[BaseGeometry, 'GeomFromText', Field, str]


def convert_to_db_value(target: GeometryLike, srid=None):
    if isinstance(target, BaseGeometry):
        return GeomFromText(dumps(target), srid)
    if isinstance(target, str):
        return GeomFromText(target, srid)
        # todo validate wkb
    if isinstance(target, Field):
        return PyPikaField(target.model_field_name)
    return target


class ComparesGeometryLike(Function):
    """
    The set of functions that compare two geometry-like objects.
    """

    name = None

    def __init__(self,
                 g1: Optional[GeometryLike] = None,
                 g2: Optional[GeometryLike] = None,
                 g1_srid=None, g2_srid=None, **kwargs
                 ):
        """
        Accepts either two geometry-like objects, or a single key-value
        where the key is a field to look up, and the value is the geometry-like
        to compare against.

        :param g1: The object to check.
        :param g2: The object you want to check contains the first.
        :param g1_srid: The optional srid of the object.
        :param g2_srid: The optional srid of the container.
        :param kwargs: An optional single key and value to filter against a field.
        """

        if g1 and g2 and not kwargs:
            g1 = convert_to_db_value(g1, g1_srid)
            g2 = convert_to_db_value(g2, g2_srid)
        elif len(kwargs) == 1:
            field, target = chain.from_iterable(kwargs.items())
            g1 = PyPikaField(field)
            g2 = convert_to_db_value(target, g2_srid)
        else:
            raise TypeError("This function accepts exactly 2 GeometryLikes or a single key-value.")

        super().__init__(self.name, g1, g2)


class Equals(ComparesGeometryLike):
    """Calculates whether the supplied GeometryLikes are the same."""
    name = "ST_Equals"


class Disjoint(ComparesGeometryLike):
    """Calculates whether the supplied GeometryLikes are disjoint."""
    name = "ST_Disjoint"


class Touches(ComparesGeometryLike):
    """Calculates whether one GeometryLike touches another."""
    name = "ST_Touches"


class Within(ComparesGeometryLike):
    """Calculates whether the first GeometryLike is completely contained in the 2nd."""
    name = "ST_Within"


class Overlaps(ComparesGeometryLike):
    """Calculates whether the first GeometryLike overlaps with the 2nd."""
    name = "ST_Overlaps"


class Contains(ComparesGeometryLike):
    """Calculates whether the first GeometryLike completely contains the 2nd."""
    name = "ST_Contains"


class Distance(ComparesGeometryLike):
    """Calculates the distance between two GeometryLikes."""
    name = "ST_Distance"


class Intersection(ComparesGeometryLike):
    """Calculates the intersecting geometry from the two GeometryLikes."""
    name = "ST_Intersection"


class Difference(ComparesGeometryLike):
    """Calculates the differing geometry from the two GeometryLikes."""
    name = "ST_Difference"


class Union(ComparesGeometryLike):
    """Calculates the union of the two GeometryLikes."""
    name = "ST_Union"


class ClosestPoint(ComparesGeometryLike):
    """Calculates the point on the first GeometryLike that is closes to the 2nd."""
    name = "ST_ClosestPoint"
