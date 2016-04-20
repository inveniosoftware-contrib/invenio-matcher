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

"""Matcher engine performing queries to the search backend."""

import six
from flask import current_app
from invenio_records import Record
from invenio_search import current_search_client
from werkzeug import import_string


def search(index, doc_type, body):
    """Perform search to external client."""
    return current_search_client.search(
        index=index, doc_type=doc_type, body=body
    )


def exact(index, doc_type, match, values, **kwargs):
    """Build an exact query and send it to Elasticsearch."""
    exact_query = _build_exact_query(match, values, **kwargs)
    return search(index, doc_type, exact_query)


def fuzzy(index, doc_type, match, values, **kwargs):
    """Build a fuzzy query and send it to Elasticsearch."""
    fuzzy_query = _build_fuzzy_query(index, doc_type, match, values, **kwargs)
    return search(index, doc_type, fuzzy_query)


def free(index, doc_type, query, **kwargs):
    """Build a free query and send it to Elasticsearch."""
    free_query = _build_free_query(query, **kwargs)
    return search(index, doc_type, free_query)


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
    return {}
