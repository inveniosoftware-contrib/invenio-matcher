# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Matcher API."""

from .core import execute, get_queries
from .errors import NoQueryDefined


def match(record, index, doc_type, queries=None, validator=None, **kwargs):
    """Find duplicates of the given record and yield results.

    This function is a generator, which returns one result at a time.
    The result is of class `MatchResult`, which is an abstract representation
    of a result returned by an engine.

    The API requires `index` and the `doc_type` for the Invenio-Search
    integration.

    NOTE: Callers might find tedious that they have to write boilerplate like
    ```
    match(r, index, doc_type)
    ```
    every single time; the idea is to encourage them to define a method in the
    client code with signature
    ```
    match_record(r)
    ```
    which wraps the previous keyword arguments.

    You can pass your own validator which is called for every result. The
    default validator filters our existing matches to avoid returning the
    same record several times.

    :return: generator over MatchResult instances.
    """
    if not queries:
        queries = get_queries(index, doc_type, **kwargs)

        if not queries:
            raise NoQueryDefined(
                'No query passed or defined in MATCHER_QUERIES.'
            )

    if not validator:
        def validator(record, result, existing_matches={}):
            """Simple deduplication validator."""
            if result.id not in existing_matches:
                existing_matches[result.id] = True
                return True
            return False

    for query in queries:
        results = execute(index, doc_type, query, record, **kwargs)

        if results:
            for result in results:
                if validator(record, result):
                    yield result
