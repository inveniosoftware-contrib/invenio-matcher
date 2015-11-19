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

"""Test Matcher's Elasticsearch engine."""

from helpers import (
    build_free_query, es_no_result, es_single_result, no_query_config,
    single_query_config, single_result
)

from invenio_matcher.errors import NoQueryDefined

from invenio_matcher.matcherext.engines.es import (
    _build_doc, _build_exact_query, _build_free_query, _build_fuzzy_query,
    _build_mlt_query, exact, free, fuzzy, queries
)

from invenio_testing import InvenioTestCase

import mock

import pytest


class TestMatcherEngineES(InvenioTestCase):

    """Matcher - test Elasticsearch engine."""

    @mock.patch('invenio_matcher.matcherext.engines.es.ES.search', es_single_result)
    def test_exact(self):
        """Send an exact query to Elasticsearch, get back a result."""
        expected = single_result()
        result = exact(index='records', doc_type='record', match='titles.title', values=['foo bar'])

        self.assertEqual(expected, result)

    @mock.patch('invenio_matcher.matcherext.engines.es.ES.search', es_no_result)
    def test_exact_no_result(self):
        """Send an exact query to Elasticsearch, get back no results."""
        expected = []
        result = exact(index='records', doc_type='record', match='titles.title', values=['foo bar'])

        self.assertEqual(expected, result)

    def test_exact_invalid_call(self):
        """Send an invalid exact query to Elasticsearch."""
        with pytest.raises(TypeError) as excinfo:
            exact()
        self.assertIn('takes exactly', str(excinfo.value))

    @mock.patch('invenio_matcher.matcherext.engines.es.ES.search', es_single_result)
    def test_fuzzy(self):
        """Send a fuzzy query to Elasticsearch, get back a result."""
        expected = single_result()
        result = fuzzy(index='records', doc_type='record', match='titles.title', values=['foo bar'])

        self.assertEqual(expected, result)

    @mock.patch('invenio_matcher.matcherext.engines.es.ES.search', es_no_result)
    def test_fuzzy_no_result(self):
        """Send a fuzzy query to Elasticsearch, get back no results."""
        expected = []
        result = fuzzy(index='records', doc_type='record', match='titles.title', values=['foo bar'])

        self.assertEqual(expected, result)

    def test_fuzzy_invalid_call(self):
        """Send an invalid fuzzy query to Elasticsearch."""
        with pytest.raises(TypeError) as excinfo:
            free()
        self.assertIn('takes exactly', str(excinfo.value))

    @mock.patch('invenio_matcher.matcherext.engines.es.ES.search', es_single_result)
    @mock.patch('invenio_matcher.matcherext.engines.es._build_free_query', build_free_query)
    def test_free(self):
        """Send a free query to Elasticsearch, get back a result."""
        expected = single_result()
        result = free(index='records', doc_type='record', query='foo.bar')

        self.assertEqual(expected, result)

    @mock.patch('invenio_matcher.matcherext.engines.es.ES.search', es_no_result)
    @mock.patch('invenio_matcher.matcherext.engines.es._build_free_query', build_free_query)
    def test_free_no_result(self):
        """Send a free query to Elasticsearch, get back no results."""
        expected = []
        result = free(index='records', doc_type='record', query='foo.bar')

        self.assertEqual(expected, result)

    def test_free_invalid_call(self):
        """Send an invalid free query to Elasticsearch."""
        with pytest.raises(TypeError) as excinfo:
            free()
        self.assertIn('takes exactly', str(excinfo.value))

    @mock.patch('invenio_matcher.matcherext.engines.es.current_app.config', single_query_config)
    def test_queries(self):
        """Get defined queries from configuration."""
        expected = [{'type': 'exact', 'match': 'titles.title'}]
        result = queries(index='records', doc_type='record')

        self.assertEqual(expected, result)

    @mock.patch('invenio_matcher.matcherext.engines.es.current_app.config', no_query_config)
    def test_no_queries(self):
        """Raise when no query is defined."""
        with pytest.raises(NoQueryDefined) as excinfo:
            queries(index='records', doc_type='record')
        self.assertIn('index records and doc_type record', str(excinfo.value))

    def test_queries_invalid_call(self):
        """Raise when the call is invalid."""
        with pytest.raises(TypeError) as excinfo:
            queries()
        self.assertIn('takes exactly', str(excinfo.value))

    def test_build_exact_query(self):
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

        self.assertEqual(expected, result)

    def test_build_exact_query_empty(self):
        """Build an exact query from an empty list of values."""
        expected = {}
        result = _build_exact_query(match='titles.title', values=[])

        self.assertEqual(expected, result)

    def test_build_exact_query_invalid_call(self):
        """Raise when the call is invalid."""
        with pytest.raises(TypeError) as excinfo:
            _build_exact_query()
        self.assertIn('takes exactly', str(excinfo.value))

    def test_build_fuzzy_query(self):
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

        self.assertEqual(_build_fuzzy_query(match='titles.title', values='foo bar', index='records', doc_type='record'), expected)

    def test_build_fuzzy_query_invalid_call(self):
        """Raise when the call is invalid."""
        with pytest.raises(TypeError) as excinfo:
            _build_fuzzy_query()
        self.assertIn('takes exactly', str(excinfo.value))

    def test_build_doc(self):
        """Build a surrogated document."""
        expected = {'titles': {'title': 'foo bar'}}
        result = _build_doc('titles.title', 'foo bar')

        self.assertEqual(expected, result)

    def test_build_mlt_query(self):
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

        self.assertEqual(_build_mlt_query(doc, min_score=2, index='records', doc_type='record'), expected)

    def test_build_mlt_query_invalid_call(self):
        """Raise when the call is invalid."""
        doc = {'titles': {'title': 'foo bar'}}

        with pytest.raises(TypeError) as excinfo:
            _build_mlt_query(doc)
        self.assertIn('takes exactly', str(excinfo.value))

    @mock.patch('invenio_matcher.matcherext.engines.es.import_string')
    def test_build_free_query(self, import_string):
        """Build a free query."""
        _build_free_query(query='foo.bar.baz')

        import_string.assert_called_with('foo.bar.baz')

    def test_build_free_query_invalid_call(self):
        """Raise when the call is invalid."""
        with pytest.raises(TypeError) as excinfo:
            _build_free_query(foo='foo')
        self.assertIn('takes exactly', str(excinfo.value))
