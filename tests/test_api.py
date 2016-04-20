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

"""Test Matcher API."""

from __future__ import absolute_import, print_function

import mock
import pytest

from invenio_matcher.api import match
from invenio_matcher.errors import NoQueryDefined
from invenio_matcher.models import MatchResult

from .helpers import duplicated_result, empty_search_result, one_search_result


def test_match_no_queries(app, simple_record):
    """Raise when no query is defined."""
    from invenio_records import Record

    with app.app_context():
        record = Record(simple_record)

        with pytest.raises(NoQueryDefined) as excinfo:
            list(match(record, index="records", doc_type="record"))
        assert 'No query defined' in str(excinfo.value)


def test_match_no_queries_config(app, simple_record):
    """Raise when no query is defined properly in config."""
    from invenio_records import Record

    app.config.update(dict(MATCHER_QUERIES={"records": {"record": []}}))
    with app.app_context():
        record = Record(simple_record)

        with pytest.raises(NoQueryDefined) as excinfo:
            list(match(record, index="records", doc_type="record"))
        assert 'No query passed or defined' in str(excinfo.value)


def test_match_with_configured_queries(app, simple_record,
                                       matcher_config, mocker):
    """Search using queries from config."""
    from invenio_records import Record
    mocker.patch('invenio_matcher.engine.search', empty_search_result)

    app.config.update(dict(MATCHER_QUERIES=matcher_config))
    with app.app_context():
        record = Record(simple_record)

        expected = []
        result = list(match(record, index="records", doc_type="record"))

        assert expected == result


def test_match_with_passed_queries(app, simple_record, mocker):
    """Search using queries passed as an argument."""
    from invenio_records import Record
    mocker.patch('invenio_matcher.engine.search', one_search_result)

    with app.app_context():
        record = Record(simple_record)
        queries = [{'type': 'exact', 'match': 'title'}]

        expected = [MatchResult(1, record, 1)]
        result = list(match(
            record,
            index="records",
            doc_type="record",
            queries=queries
        ))
        assert expected == result


def test_default_deduplication_validator(app, simple_record, mocker):
    """Make sure default deduplication validator works."""
    from invenio_records import Record
    mocker.patch('invenio_matcher.api.execute', duplicated_result)

    with app.app_context():
        record = Record(simple_record)
        queries = [{'type': 'exact', 'match': 'title'}]

        expected = [MatchResult(1, record, 1)]
        result = list(match(
            record,
            index="records",
            doc_type="record",
            queries=queries,
            validator=None,
        ))

        assert expected == result

        # Test the same again to see if validator resets
        expected = [MatchResult(1, record, 1)]
        result = list(match(
            record,
            index="records",
            doc_type="record",
            queries=queries,
            validator=None,
        ))

        assert expected == result


def test_match_with_validator(app, simple_record, mocker):
    """Validate results with a validator function."""
    from invenio_records import Record
    mocker.patch('invenio_matcher.engine.search', one_search_result)

    with app.app_context():
        record = Record(simple_record)
        queries = [{'type': 'exact', 'match': 'title'}]

        def validator(record, result):
            return record['title'] == 'bar foo'

        expected = []
        result = list(match(
            record,
            index="records",
            doc_type="record",
            queries=queries,
            validator=validator,
        ))

        assert expected == result
