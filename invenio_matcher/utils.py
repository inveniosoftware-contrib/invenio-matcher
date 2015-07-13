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

"""Matcher utility functions."""

import six


def build_doc(mapping):
    doc = {}

    for key, values in six.iteritems(mapping):
        tmp = doc
        parts = key.split('.')

        for part in parts[:-1]:
            tmp = tmp.setdefault(part, {})

        tmp[parts[-1]] = values

    return doc


def build_fuzzy_query(mapping, index, doc_type):
    doc = build_doc(mapping)
    query = {
        'min_score': 1,
        'query': {
            'more_like_this': {
                'docs': [
                    {
                        '_index': index,
                        '_type': doc_type,
                        'doc': doc
                    }
                ]
            }
        },
        'min_term_freq': 1,
        'min_doc_freq': 1
    }

    return query


def build_or_query(key, values):
    query = {
        'query': {
            'filtered': {
                'filter': {
                    'or': []
                }
            }
        }
    }

    for value in values:
        subquery  = {
            'query': {
                'filtered': { 
                    'filter': { 
                        'term': {
                            key: value
                        }
                    }
                }
            }
        }
        query['query']['filtered']['filter']['or'].append(subquery)

    return query


def build_exact_query(mapping, index, doc_type):
    query = {
        'query': {
            'filtered': {
                'filter': {
                    'and': []
                }
            }
        }
    }

    for key, values in six.iteritems(mapping):
        subquery = build_or_query(key, values)
        query['query']['filtered']['filter']['and'].append(subquery)

    return query

