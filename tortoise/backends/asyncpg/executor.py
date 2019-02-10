from itertools import count
from typing import List, Any

from pypika import Parameter, Table

from tortoise.backends.base.executor import BaseExecutor
from tortoise.function import Function


class AsyncpgExecutor(BaseExecutor):

    EXPLAIN_PREFIX = 'EXPLAIN (FORMAT JSON, VERBOSE)'

    def _prepare_insert_statement(self, columns: List[str], values: List[Any]) -> str:
        counter = count(1)

        values = [
            value.parameterize(lambda: f"${next(counter)}")
            if isinstance(value, Function)
            else Parameter(f"${next(counter)}")
            for value in values
        ]

        return str(
            self.db.query_class
                .into(Table(self.model._meta.table))
                .columns(*columns)
                .insert(*values)
                .returning('id')
        )
