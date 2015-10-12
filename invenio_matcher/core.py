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

"""Matcher core."""

import copy

import six

from .engine import exact, free, fuzzy, queries
from .errors import InvalidQuery, NotImplementedQuery


def execute(query, record, **kwargs):
    """Parse a query and send it to the engine."""
    _type, match, values, extras = _parse(query, record)
    _kwargs = _merge(kwargs, extras)

    if _type == 'exact':
        return exact(match=match, values=values, **_kwargs)
    elif _type == 'fuzzy':
        return fuzzy(match=match, values=values, **_kwargs)
    elif _type == 'free':
        return free(match=match, values=values, **_kwargs)
    else:
        raise NotImplementedQuery('Query of type {_type} is not currently'
                                  ' implemented.'.format(_type=_type))


def get_queries(**kwargs):
    """Get defined queries from the engine."""
    return queries(**kwargs)


def _merge(d1, d2):
    """Merge two dictionaries."""
    result = copy.deepcopy(d1)
    result.update(d2)

    return result


def _parse(query, record):
    """Parse a query and extract values from record."""
    try:
        _type = query['type']
        match = query['match']
    except KeyError:
        raise InvalidQuery('Keys "type" and "match" not defined in query'
                           ' {query}'.format(query=query))

    values = record[match]
    match = query.get('with', match)
    extras = {k: v for k, v in six.iteritems(
        query) if k not in set(['type', 'match', 'with'])}

    return _type, match, values, extras
