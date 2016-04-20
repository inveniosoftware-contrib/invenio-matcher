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

"""Test Matcher's Elasticsearch engine."""

from __future__ import absolute_import, print_function

import mock

from invenio_matcher.engine import _build_doc, _build_exact_query, \
    _build_free_query, _build_fuzzy_query, _build_mlt_query


def test_build_exact_query():
    """Build an exact query."""
    expected = {
        'query': {
            'filtered': {
                'filter': {
                    'or': [
                        {
                            'query': {
                                'filtered': {
                                    'filter': {
                                        'term': {
                                            'titles.title': 'foo'
                                        }
                                    }
                                }
                            }
                        },
                        {
                            'query': {
                                'filtered': {
                                    'filter': {
                                        'term': {
                                            'titles.title': 'bar'
                                        }
                                    }
                                }
                            }
                        }
                    ]
                }
            }
        }
    }
    result = _build_exact_query(match='titles.title', values=['foo', 'bar'])

    assert expected == result


def test_build_exact_query_empty():
    """Build an exact query from an empty list of values."""
    expected = {}
    result = _build_exact_query(match='titles.title', values=[])

    assert expected == result


def test_build_fuzzy_query():
    """Build a fuzzy query."""
    expected = {
        'min_score': 1,
        'query': {
            'more_like_this': {
                'docs': [
                    {
                        '_index': 'records',
                        '_type': 'record',
                        'doc': {
                            'titles': {
                                'title': 'foo bar'
                            }
                        }
                    }
                ]
            }
        },
        'min_term_freq': 1,
        'min_doc_freq': 1
    }

    result = _build_fuzzy_query(
        match='titles.title',
        values='foo bar',
        index='records',
        doc_type='record'
    )
    assert result == expected


def test_build_doc():
    """Build a surrogated document."""
    expected = {'titles': {'title': 'foo bar'}}
    result = _build_doc('titles.title', 'foo bar')

    assert expected == result


def test_build_mlt_query():
    """Build an mlt query."""
    doc = {'titles': {'title': 'foo bar'}}
    expected = {
        'min_score': 2,
        'query': {
            'more_like_this': {
                'docs': [
                    {
                        '_index': 'records',
                        '_type': 'record',
                        'doc': {
                            'titles': {
                                'title': 'foo bar'
                            }
                        }
                    }
                ]
            }
        },
        'min_term_freq': 1,
        'min_doc_freq': 1
    }
    result = _build_mlt_query(
        doc,
        min_score=2,
        index='records',
        doc_type='record'
    )
    assert result == expected


@mock.patch('invenio_matcher.engine.import_string')
def test_build_free_query(import_string):
    """Build a free query."""
    _build_free_query(query='foo.bar.baz')
    import_string.assert_called_with('foo.bar.baz')
