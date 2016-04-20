# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
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

"""Matcher core."""

import copy

import six
from flask import current_app
from invenio_records import Record

from .engine import exact, free, fuzzy
from .errors import InvalidQuery, NoQueryDefined, NotImplementedQuery
from .models import MatchResult


def execute(index, doc_type, query, record, **kwargs):
    """Parse a query and send it to the engine, returning a list of hits."""
    _type, match, values, extras = _parse(query, record)

    if not values:
        # No values in the record to match with
        return []

    _kwargs = _merge(kwargs, extras)

    if _type == 'exact':
        result = exact(index, doc_type, match=match, values=values, **_kwargs)
    elif _type == 'fuzzy':
        result = fuzzy(index, doc_type, match=match, values=values, **_kwargs)
    elif _type == 'free':
        result = free(index, doc_type, query, **_kwargs)
    else:
        raise NotImplementedQuery('Query of type {_type} is not currently'
                                  ' implemented.'.format(_type=_type))
    return _build_result(result['hits']['hits'])


def get_queries(index, doc_type, **kwargs):
    """Return queries defined for the given index and doc_type."""
    MATCHER_QUERIES = current_app.config.get('MATCHER_QUERIES')
    try:
        return MATCHER_QUERIES[index][doc_type]
    except (KeyError, TypeError):
        raise NoQueryDefined('No query defined for index {index} and doc_type'
                             ' {doc_type} in MATCHER_QUERIES.'.format(
                                 index=index, doc_type=doc_type))


def _build_result(hits):
    return [MatchResult(
        hit['_id'],
        Record(hit['_source']),
        hit['_score']) for hit in hits
    ]


def _merge(d1, d2):
    """Merge two dictionaries."""
    result = copy.deepcopy(d1)
    result.update(d2)

    return result


def _get_values(record, match):
    """Retrieve the values from the record.

    Ensures that the values will be a list, since this is what the
    rest of the code expects.
    """
    result = record.get(match, [])
    if not result:
        return []
    if not isinstance(result, list):
        result = [result]

    return result


def _parse(query, record):
    """Parse a query and extract values from record."""
    try:
        _type = query['type']
        match = query['match']
    except KeyError:
        raise InvalidQuery('Keys "type" and "match" not defined in query'
                           ' {query}'.format(query=query))

    # XXX(jacquerie): This allows the user to pass directly the values to be
    # retrieved from the record. This is an advanced feature, therefore is
    # not advertised in the public API.
    values = query.get('values', _get_values(record, match))
    match = query.get('with', match)
    extras = {k: v for k, v in six.iteritems(
        query) if k not in set(['type', 'match', 'with', 'values'])}

    return _type, match, values, extras
