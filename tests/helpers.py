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

"""Matcher test helpers."""

import imp

from invenio_base.wrappers import lazy_import

from invenio_matcher.models import MatchResult


Record = lazy_import('invenio_records.api.Record')


def data():
    """Represent a record."""
    return {'titles': [{'title': 'foo bar'}]}


def simple_data():
    """Represent a simple record."""
    return {'title': 'foo bar'}


def no_results(query, record, **kwargs):
    """Return no results."""
    return []


def single_result(query, record, **kwargs):
    """Return a single result."""
    return [MatchResult(Record(data()), 1)]


def no_queries(**kwargs):
    """Return no queries."""
    return []


def single_query(**kwargs):
    """Return a single query."""
    return [{'type': 'exact', 'match': 'titles.title'}]


no_engine_config = {}


single_engine_config = {'MATCHER_ENGINE': 'foo'}


single_engine_engines = {'foo': 'bar'}


def get_engine():
    """Mock an engine module.

    Yes, you can do this. See http://stackoverflow.com/a/3799609/374865
    for more details, and laugh maniacally with me.
    """
    engine = imp.new_module('engine')
    engine_code = '''
def exact(**kwargs):
    return 'exact'

def fuzzy(**kwargs):
    return 'fuzzy'

def free(**kwargs):
    return 'free'

def queries(**kwargs):
    return 'queries'
    '''
    exec engine_code in engine.__dict__

    return engine
