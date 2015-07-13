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

from invenio.ext.es import es

from .errors import InvalidQuery
from .utils import build_exact_query, build_fuzzy_query


def exact(mapping, index, doc_type):
    es_query = build_exact_query(mapping, index, doc_type)
    result = es.search(body=es_query, index=index, doc_type=doc_type)

    if result['hits']['total'] == 0:
        return None
    else:
        return result['hits']['hits']


def fuzzy(mapping, index, doc_type):
    es_query = build_fuzzy_query(mapping, index, doc_type)
    result = es.search(body=es_query, index=index, doc_type=doc_type)

    if result['hits']['total'] == 0:
        return None
    else:
        return result['hits']['hits']

# http://stackoverflow.com/a/10824420/374865
def flatten(container):
    for i in container:
        if isinstance(i, list) or isinstance(i, tuple):
            for j in flatten(i):
                yield j
        else:
            yield i


def walk(parts, record):
    if isinstance(record, list):
        return [walk(parts, el) for el in record]
    else:
        if len(parts) == 1:
            return record[parts[0]]
        else:
            return walk(parts[1:], record[parts[0]])


def get_values(path, record):
    return list(flatten(walk(path.split('.'), record)))


def parse(query, record):
    try:
        type_ = query['type']

        if query.get('with', None):
            key = query['with']
        else:
            key = query['match']

        values = get_values(query['match'], record)
        mapping = {key: values}

        return type_, mapping
    except KeyError:
        raise InvalidQuery('TODO')


def execute(query, record, index, doc_type):
    type_, mapping = parse(query, record)

    if type_ == 'exact':
        return exact(mapping, index, doc_type)
    elif type_ == 'fuzzy':
        return fuzzy(mapping, index, doc_type)
    else:
        raise NotImplementedError
