# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017 CERN.
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

"""Matcher utils."""

from __future__ import absolute_import, division, print_function

import re


SPLIT_KEY_PATTERN = re.compile('\.|\[')


def get_value(record, key, default=None):
    """Return item as `dict.__getitem__` but using 'smart queries'.

    .. note::
        Accessing one value in a normal way, meaning d['a'], is almost as
        fast as accessing a regular dictionary. But using the special
        name convention is a bit slower than using the regular access:
        .. code-block:: python
            >>> %timeit x = dd['a[0].b']
            100000 loops, best of 3: 3.94 us per loop
            >>> %timeit x = dd['a'][0]['b']
            1000000 loops, best of 3: 598 ns per loop
    """
    def getitem(k, v, default):
        if isinstance(v, dict):
            return v[k]
        elif ']' in k:
            k = k[:-1].replace('n', '-1')
            # Work around for list indexes and slices
            try:
                return v[int(k)]
            except IndexError:
                return default
            except ValueError:
                return v[slice(*map(
                    lambda x: int(x.strip()) if x.strip() else None,
                    k.split(':')
                ))]
        else:
            tmp = []
            for inner_v in v:
                try:
                    tmp.append(getitem(k, inner_v, default))
                except KeyError:
                    continue
            return tmp

    # Check if we are using python regular keys
    try:
        return record[key]
    except KeyError:
        pass

    keys = SPLIT_KEY_PATTERN.split(key)
    value = record
    for k in keys:
        try:
            value = getitem(k, value, default)
        except KeyError:
            return default
    return value
