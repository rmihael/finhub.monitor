from datetime import datetime
from itertools import chain, islice
from typing import List

import boto3


class KnownLoansDAO:
    def __init__(self, table_name: str) -> None:
        self._table_name = table_name
        self._raw_table = None

    @staticmethod
    def _chunks(iterable, size=100):
        """
        Split an iterable into chunks without pre-walking it

        :param iterable: Some iterable that we should split in to chunks of iterable
        :type iterable: collections.Iterable

        :param size: Chunk size by default 10
        :type size: int

        :return: Generator of generators split by provided size
        :rtype: collections.Iterable[collections.Iterable]
        """
        iterator = iter(iterable)
        for first in iterator:
            yield chain([first], islice(iterator, size - 1))

    @property
    def _table(self):
        if self._raw_table is None:
            self._raw_table = boto3.resource("dynamodb").Table(self._table_name)
        return self._raw_table

    def filter_out_known_ids(self, ids: List[str]) -> List[str]:
        known_ids = set()
        for chunk in self._chunks(ids):
            response = self._table.meta.client.batch_get_item(RequestItems={
                self._table_name: {
                    'Keys': [{'id': i} for i in chunk]
                }
            })
            items = response['Responses'][self._table_name]
            known_ids.update(i['id'] for i in items)
        return [i for i in ids if i not in known_ids]

    def memorize_loans(self, ids: List[str], when: datetime) -> None:
        with self._table.batch_writer() as batch:
            for i in ids:
                batch.put_item(Item={'id': i, 'when': int(when.timestamp())})
