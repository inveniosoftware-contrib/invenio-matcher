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

"""Test Matcher core."""

from __future__ import absolute_import, print_function

import mock
import pytest

from invenio_matcher.core import _merge, _parse, execute, get_queries
from invenio_matcher.errors import InvalidQuery, NotImplementedQuery
from invenio_records import Record

from .helpers import empty_search_result


def test_queries(app, matcher_config):
    """Get defined queries from configuration."""
    app.config.update(dict(MATCHER_QUERIES=matcher_config))
    with app.app_context():
        expected = [{'type': 'exact', 'match': 'title'}]
        result = get_queries(index='records', doc_type='record')

        assert expected == result


def test_execute_exact(app, simple_record, mocker):
    """Dispatch the query of type exact."""
    mocker.patch('invenio_matcher.engine.search', empty_search_result)

    with app.app_context():
        query = {'type': 'exact', 'match': 'title'}
        index = "records"
        doc_type = "record"

        record = Record(simple_record)

        expected = []
        result = execute(index, doc_type, query, record)

        assert result == expected


def test_execute_fuzzy(app, simple_record, mocker):
    """Dispatch the query of type fuzzy."""
    mocker.patch('invenio_matcher.engine.search', empty_search_result)

    with app.app_context():
        query = {'type': 'fuzzy', 'match': 'title'}
        index = "records"
        doc_type = "record"

        record = Record(simple_record)

        expected = []
        result = execute(index, doc_type, query, record)

        assert result == expected


def test_execute_free(app, simple_record, mocker):
    """Dispatch the query of type free."""
    mocker.patch('invenio_matcher.engine.search', empty_search_result)

    with app.app_context():
        query = {'type': 'free', 'match': 'title'}
        index = "records"
        doc_type = "record"
        record = Record(simple_record)

        expected = []
        result = execute(index, doc_type, query, record)

        assert result == expected


def test_execute_missing_type(app, simple_record):
    """Handle things when bad query type is passed."""
    with app.app_context():
        query = {'type': 'banana', 'match': 'title'}
        index = "records"
        doc_type = "record"
        record = Record(simple_record)

        with pytest.raises(NotImplementedQuery):
            result = execute(index, doc_type, query, record)


def test_execute_missing_data(app):
    """Handle missing data in record."""
    with app.app_context():
        query = {'type': 'exact', 'match': 'title'}
        index = "records"
        doc_type = "record"
        record = Record({})

        assert execute(index, doc_type, query, record) == []


def test_execute_missing_data_in_key(app):
    """Handle no data in key of record"""
    with app.app_context():
        query = {'type': 'exact', 'match': 'title'}
        index = "records"
        doc_type = "record"
        record = Record({'title': None})

        assert execute(index, doc_type, query, record) == []


def test_get_queries(app):
    """Dispatch the retrieval of queries."""
    with app.app_context():
        index = "records"
        doc_type = "record"
        app.config.update({"MATCHER_QUERIES": {
            index: {doc_type: [{'type': 'exact', 'match': 'titles.title'}]}
        }})
        expected = [{'type': 'exact', 'match': 'titles.title'}]
        result = get_queries(index, doc_type)

        assert expected == result


def test_parse_simple_query(app, simple_record):
    """Parse a simple query."""
    with app.app_context():
        query = {'type': 'exact', 'match': 'title'}
        record = Record(simple_record)

        _type, match, values, extras = _parse(query, record)

        assert _type == 'exact'
        assert match == 'title'
        assert values == ['foo bar']
        assert extras == {}


def test_parse_query_with_with(app, simple_record):
    """Parse a query with the 'with' keyword."""
    with app.app_context():
        query = {'type': 'exact', 'match': 'title', 'with': 'titles.title'}
        record = Record(simple_record)

        _type, match, values, extras = _parse(query, record)

        assert _type == 'exact'
        assert match == 'titles.title'
        assert values == ['foo bar']
        assert extras == {}


def test_parse_query_with_extras(app, simple_record):
    """Parse a query preserving other keyword arguments."""
    with app.app_context():
        query = {'type': 'exact', 'match': 'title', 'foo': 'bar'}
        record = Record(simple_record)

        _type, match, values, extras = _parse(query, record)

        assert _type == 'exact'
        assert match == 'title'
        assert values == ['foo bar']
        assert extras == {'foo': 'bar'}


def test_parse_query_can_override_values(app, simple_record):
    """Parse a query overriding the extracted values."""
    with app.app_context():
        query = {'type': 'exact', 'match': 'title', 'values': ['qux quux']}
        record = Record(simple_record)

        _type, match, values, extras = _parse(query, record)

        assert _type == 'exact'
        assert match == 'title'
        assert values == ['qux quux']
        assert extras == {}


def test_parse_invalid_query(app, simple_record):
    """Raise for malformed queries."""
    with app.app_context():
        query = {'type': 'exact'}
        record = Record(simple_record)

        with pytest.raises(InvalidQuery) as excinfo:
            _type, match, values, extras = _parse(query, record)
        assert 'not defined in query' in str(excinfo.value)


def test_parse_query_with_invalid_path(app, simple_record):
    """Parse a query on a record with invalid_path.

    We want to make sure that, even when we give an invalid path
    to the Record API we get back an empty list.
    """
    with app.app_context():
        query = {'type': 'exact', 'match': 'titles.title'}
        record = Record(simple_record)

        _type, match, values, extras = _parse(query, record)

        assert _type == 'exact'
        assert match == 'titles.title'
        assert values == []
        assert extras == {}


def test_merge():
    """Merge two dictionaries."""
    d1 = {'foo': 'foo', 'bar': 'bar'}
    d2 = {'baz': 'baz'}

    assert _merge(d1, d2) == {'foo': 'foo', 'bar': 'bar', 'baz': 'baz'}
