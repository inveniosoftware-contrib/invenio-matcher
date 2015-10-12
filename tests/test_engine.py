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

"""Test Matcher engine dispatcher."""

from helpers import (
    get_engine, no_engine_config, single_engine_config, single_engine_engines
)

from invenio_matcher.engine import _get_engine, exact, free, fuzzy, queries
from invenio_matcher.errors import NoEngineDefined

from invenio_testing import InvenioTestCase

import mock

import pytest


class TestMatcherEngine(InvenioTestCase):

    """Matcher - test engine."""

    @mock.patch('invenio_matcher.engine._get_engine', get_engine)
    def test_exact(self):
        """Dispatch the exact method."""
        expected = 'exact'
        result = exact()

        self.assertEqual(expected, result)

    @mock.patch('invenio_matcher.engine._get_engine', get_engine)
    def test_fuzzy(self):
        """Dispatch the fuzzy method."""
        expected = 'fuzzy'
        result = fuzzy()

        self.assertEqual(expected, result)

    @mock.patch('invenio_matcher.engine._get_engine', get_engine)
    def test_free(self):
        """Dispatch the free method."""
        expected = 'free'
        result = free()

        self.assertEqual(expected, result)

    @mock.patch('invenio_matcher.engine._get_engine', get_engine)
    def test_queries(self):
        """Dispatch the queries method."""
        expected = 'queries'
        result = queries()

        self.assertEqual(expected, result)

    @mock.patch('invenio_matcher.engine.engines', single_engine_engines)
    @mock.patch('invenio_matcher.engine.current_app.config', single_engine_config)
    def test_get_engine(self):
        """Get the defined engine."""
        expected = 'bar'
        result = _get_engine()

        self.assertEqual(expected, result)

    @mock.patch('invenio_matcher.engine.current_app.config', no_engine_config)
    def test_invalid_get_engine(self):
        """Raise error when forgetting to define an engine."""
        with pytest.raises(NoEngineDefined) as excinfo:
            _get_engine()
        self.assertIn('registry, or not defined', str(excinfo.value))
