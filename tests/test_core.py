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

"""Test Matcher core."""

from helpers import data, simple_data, single_query

from invenio_base.wrappers import lazy_import

from invenio_matcher.core import _merge, _parse, execute, get_queries
from invenio_matcher.errors import InvalidQuery, NotImplementedQuery

from invenio_testing import InvenioTestCase

import mock

import pytest


Record = lazy_import('invenio_records.api.Record')


class TestMatcherCore(InvenioTestCase):

    """Matcher: test core."""

    def setup_class(self):
        self.data = data()
        self.simple_data = simple_data()

    @mock.patch('invenio_matcher.core.exact')
    def test_execute_exact(self, exact):
        """Dispatch the query of type exact."""
        query = {'type': 'exact', 'match': 'titles.title'}
        record = Record(self.data)

        execute(query, record)

        exact.assert_called_with(match='titles.title', values=['foo bar'])

    @mock.patch('invenio_matcher.core.fuzzy')
    def test_execute_fuzzy(self, fuzzy):
        """Dispatch the query of type fuzzy."""
        query = {'type': 'fuzzy', 'match': 'titles.title'}
        record = Record(self.data)

        execute(query, record)

        fuzzy.assert_called_with(match='titles.title', values=['foo bar'])

    @mock.patch('invenio_matcher.core.free')
    def test_execute_free(self, free):
        """Dispatch the query of type free."""
        query = {'type': 'free', 'match': 'titles.title', 'query': 'foo.bar.baz'}
        record = Record(self.data)

        execute(query, record)

        free.assert_called_with(match='titles.title', values=['foo bar'], query='foo.bar.baz')

    def test_execute_not_implemented(self):
        """Raise for other types."""
        query = {'type': 'foobar', 'match': 'titles.title'}
        record = Record(self.data)

        with pytest.raises(NotImplementedQuery) as excinfo:
            execute(query, record)
        self.assertIn('type foobar', str(excinfo.value))

    @mock.patch('invenio_matcher.core.exact')
    def test_execute_no_values(self, exact):
        """In case the record does not contain the match value."""
        query = {'type': 'exact', 'match': 'titles.title'}
        record = Record({})

        res = execute(query, record)

        assert not exact.called, 'exact function should not have been called'
        assert res == []

    @mock.patch('invenio_matcher.core.queries', single_query)
    def test_get_queries(self):
        """Dispatch the retrieval of queries."""
        expected = [{'type': 'exact', 'match': 'titles.title'}]
        result = get_queries(foo='foo')

        self.assertEqual(expected, result)

    def test_parse_simple_query(self):
        """Parse a simple query."""
        query = {'type': 'exact', 'match': 'titles.title'}
        record = Record(self.data)

        _type, match, values, extras = _parse(query, record)

        self.assertEqual(_type, 'exact')
        self.assertEqual(match, 'titles.title')
        self.assertEqual(values, ['foo bar'])
        self.assertEqual(extras, {})

    def test_parse_query_with_with(self):
        """Parse a query with the 'with' keyword."""
        query = {'type': 'exact', 'match': 'titles.title', 'with': 'oldtitles.title'}
        record = Record(self.data)

        _type, match, values, extras = _parse(query, record)

        self.assertEqual(_type, 'exact')
        self.assertEqual(match, 'oldtitles.title')
        self.assertEqual(values, ['foo bar'])
        self.assertEqual(extras, {})

    def test_parse_query_with_extras(self):
        """Parse a query preserving other keyword arguments."""
        query = {'type': 'exact', 'match': 'titles.title', 'foo': 'bar'}
        record = Record(self.data)

        _type, match, values, extras = _parse(query, record)

        self.assertEqual(_type, 'exact')
        self.assertEqual(match, 'titles.title')
        self.assertEqual(values, ['foo bar'])
        self.assertEqual(extras, {'foo': 'bar'})

    def test_parse_query_can_override_values(self):
        """Parse a query overriding the extracted values."""
        query = {'type': 'exact', 'match': 'titles.title', 'values': ['qux quux']}
        record = Record(self.data)

        _type, match, values, extras = _parse(query, record)

        self.assertEqual(_type, 'exact')
        self.assertEqual(match, 'titles.title')
        self.assertEqual(values, ['qux quux'])
        self.assertEqual(extras, {})

    def test_parse_invalid_query(self):
        """Raise for malformed queries."""
        query = {'type': 'exact'}
        record = Record(self.data)

        with pytest.raises(InvalidQuery) as excinfo:
            _type, match, values, extras = _parse(query, record)
        self.assertIn('not defined in query', str(excinfo.value))

    def test_parse_query_with_invalid_path(self):
        """Parse a query on a record with invalid_path.

        We want to make sure that, even when we give an invalid path
        to the Record API we get back an empty list.
        """
        query = {'type': 'exact', 'match': 'titles.title'}
        record = Record(self.simple_data)

        _type, match, values, extras = _parse(query, record)

        self.assertEqual(_type, 'exact')
        self.assertEqual(match, 'titles.title')
        self.assertEqual(values, [])
        self.assertEqual(extras, {})

    def test_parse_query_without_lists(self):
        """Parse a query on a record without lists.

        We want to make sure that, even when the Record API does not
        return a list, we are getting a list for the 'values' variable.
        """
        query = {'type': 'exact', 'match': 'title'}
        record = Record(self.simple_data)

        _type, match, values, extras = _parse(query, record)

        self.assertEqual(_type, 'exact')
        self.assertEqual(match, 'title')
        self.assertEqual(values, ['foo bar'])
        self.assertEqual(extras, {})

    def test_merge(self):
        """Merge two dictionaries."""
        d1 = {'foo': 'foo', 'bar': 'bar'}
        d2 = {'baz': 'baz'}

        self.assertEqual(_merge(d1, d2), {'foo': 'foo', 'bar': 'bar', 'baz': 'baz'})
