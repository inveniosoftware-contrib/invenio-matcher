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

"""Matcher engines test helpers."""

from invenio_base.wrappers import lazy_import

from invenio_matcher.models import MatchResult


Record = lazy_import('invenio_records.api.Record')


no_query_config = {
    'MATCHER_QUERIES': {
        'es': {}
    }
}


single_query_config = {
    'MATCHER_QUERIES': {
        'es': {
            'records': {
                'record': [
                    {'type': 'exact', 'match': 'titles.title'}
                ]
            }
        }
    }
}


def es_no_result(**kwargs):
    """Return no results from Elasticsearch."""
    return {'hits': {'hits': []}}


def es_single_result(**kwargs):
    """Return a single result from Elasticsearch."""
    return {
        'hits': {
            'hits': [
                {
                    '_source': {'titles': [{'title': 'foo bar'}]},
                    '_score': 1.0
                }
            ]
        }
    }


def simple_data():
    """Represent a simple record."""
    return {'titles': [{'title': 'foo bar'}]}


def single_result(**kwargs):
    """Return a single result."""
    return [MatchResult(Record(simple_data()), 1)]


def build_free_query(query, **kwargs):
    """Build a free query.

    We don't actually need to build the query, since Elasticsearch's
    response is mocked anyway, but we need to avoid the import_string.
    """
    pass
