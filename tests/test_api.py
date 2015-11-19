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

"""Test Matcher API."""

from helpers import (
    data, no_queries, no_results, single_query, single_result
)

from invenio_base.wrappers import lazy_import

from invenio_matcher.api import match
from invenio_matcher.errors import NoQueryDefined
from invenio_matcher.models import MatchResult

from invenio_testing import InvenioTestCase

import mock

import pytest


Record = lazy_import('invenio_records.api.Record')


class TestMatcherAPI(InvenioTestCase):

    """Matcher: test API."""

    def setup_class(self):
        """Load data for a simple record."""
        self.data = data()

    @mock.patch('invenio_matcher.api.get_queries', no_queries)
    def test_match_no_queries(self):
        """Raise when no query are defined."""
        record = Record(self.data)

        with pytest.raises(NoQueryDefined) as excinfo:
            list(match(record))
        self.assertIn('passed or defined', str(excinfo.value))

    @mock.patch('invenio_matcher.api.get_queries', single_query)
    @mock.patch('invenio_matcher.api.execute', no_results)
    def test_match_with_configured_queries(self):
        """Search using configured queries."""
        record = Record(self.data)

        expected = []
        result = list(match(record))

        self.assertEqual(expected, result)

    @mock.patch('invenio_matcher.api.execute', single_result)
    def test_match_with_passed_queries(self):
        """Search using queries passed as an argument."""
        record = Record(self.data)
        queries = [{'type': 'exact', 'match': 'titles.title'}]

        expected = [MatchResult(record, 1)]
        result = list(match(record, queries=queries))

        self.assertEqual(expected, result)

    @mock.patch('invenio_matcher.api.execute', single_result)
    def test_match_with_validator(self):
        """Validate results with a validator function."""
        record = Record(self.data)
        queries = [{'type': 'exact', 'match': 'titles.title'}]

        def validator(record, result):
            return record['titles'][0]['title'] == 'bar foo'

        expected = []
        result = list(match(record, queries=queries, validator=validator))

        self.assertEqual(expected, result)
