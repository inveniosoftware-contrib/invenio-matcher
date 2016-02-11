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

"""Invenio Matcher Elasticsearch engine."""

from flask import current_app

from invenio_base.wrappers import lazy_import

from invenio_matcher.errors import NoQueryDefined
from invenio_matcher.models import MatchResult

import six

from werkzeug.utils import import_string


ES = lazy_import('invenio_ext.es.es')
Record = lazy_import('invenio_records.api.Record')


def exact(index, doc_type, match, values, **kwargs):
    """Build an exact query and send it to Elasticsearch."""
    exact_query = _build_exact_query(match, values, **kwargs)
    result = ES.search(index=index, doc_type=doc_type, body=exact_query)
    return _build_result(result['hits']['hits'])


def fuzzy(index, doc_type, match, values, **kwargs):
    """Build a fuzzy query and send it to Elasticsearch."""
    fuzzy_query = _build_fuzzy_query(index, doc_type, match, values, **kwargs)
    result = ES.search(index=index, doc_type=doc_type, body=fuzzy_query)
    return _build_result(result['hits']['hits'])


def free(index, doc_type, query, **kwargs):
    """Build a free query and send it to Elasticsearch."""
    free_query = _build_free_query(query, **kwargs)
    result = ES.search(index=index, doc_type=doc_type, body=free_query)
    return _build_result(result['hits']['hits'])


def queries(index, doc_type, **kwargs):
    """Return queries defined for the given index and doc_type."""
    MATCHER_QUERIES = current_app.config.get('MATCHER_QUERIES')

    try:
        return MATCHER_QUERIES['es'][index][doc_type]
    except KeyError:
        raise NoQueryDefined('No query defined for index {index} and doc_type'
                             ' {doc_type} in MATCHER_QUERIES.'.format(
                                 index=index, doc_type=doc_type))


def _build_exact_query(match, values, **kwargs):
    """Build an exact query."""
    if values == []:
        return {}

    result = {
        'query': {
            'filtered': {
                'filter': {
                    'or': []
                }
            }
        }
    }

    for value in values:
        subquery = {
            'query': {
                'filtered': {
                    'filter': {
                        'term': {
                            match: value
                        }
                    }
                }
            }
        }

        result['query']['filtered']['filter']['or'].append(subquery)

    return result


def _build_result(hits):
    return [MatchResult(
        hit['_id'],
        Record(hit['_source']),
        hit['_score']) for hit in hits
    ]


def _build_fuzzy_query(index, doc_type, match, values, **kwargs):
    """Build a fuzzy query."""
    doc = _build_doc(match, values)
    result = _build_mlt_query(doc, index, doc_type, **kwargs)

    return result


def _build_doc(match, values):
    """Build a fake document to use in an mlt query."""
    result = {}

    tmp = result

    parts = match.split('.')
    for part in parts[:-1]:
        tmp = tmp.setdefault(part, {})

    tmp[parts[-1]] = values

    return result


def _build_mlt_query(doc, index, doc_type, **kwargs):
    """Build an mlt query."""
    min_score = kwargs.get('min_score', 1)
    min_doc_freq = kwargs.get('min_doc_freq', 1)
    min_term_freq = kwargs.get('min_term_freq', 1)

    return {
        'min_score': min_score,
        'query': {
            'more_like_this': {
                'docs': [
                    {
                        '_index': index,
                        '_type': doc_type,
                        'doc': doc
                    }
                ]
            }
        },
        'min_doc_freq': min_doc_freq,
        'min_term_freq': min_term_freq
    }


def _build_free_query(query, **kwargs):
    """Build a free query.

    FIXME(jacquerie): instead of a blind import_string we could fetch
    the query from a registry of queries.
    """
    if isinstance(query, six.string_types):
        query_func = import_string(query)

    return query_func(**kwargs)
