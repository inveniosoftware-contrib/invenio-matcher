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

"""Test Matcher utils."""

from invenio.testsuite import InvenioTestCase

from invenio_matcher.utils import build_doc
from invenio_matcher.utils import build_fuzzy_query
from invenio_matcher.utils import build_or_query
from invenio_matcher.utils import build_exact_query


class TestMatcherUtils(InvenioTestCase):
    
    """Matcher - TODO."""

    def test_build_doc(self):
        mapping = {'title.title': 'foo', 'author.full_name': 'bar'}
        expected = {'title': {'title': 'foo'}, 'author': {'full_name': 'bar'}}

        assert build_doc(mapping) == expected


    def test_build_fuzzy_query(self):
        mapping = {'title.title': 'foo', 'author.full_name': 'bar'}
        expected = {
            'min_score': 1,
            'query': {
                'more_like_this': {
                    'docs': [
                        {
                            '_index': 'records',
                            '_type': 'record',
                            'doc': {
                                'title': {
                                    'title': 'foo'
                                },
                                'author': {
                                    'full_name': 'bar'
                                }
                            }
                        }
                    ]
                }
            },
            'min_term_freq': 1,
            'min_doc_freq': 1
        }

        assert build_fuzzy_query(mapping, 'records', 'record') == expected

    def test_build_or_query(self):
        expected = {
            'query': {
                'filtered': {
                    'filter': {
                        'or': [
                            {
                                'query': {
                                    'filtered': {
                                        'filter': {
                                            'term': {
                                                'foo': 'bar'
                                            }
                                        }
                                    }
                                }
                            },
                            {
                                'query': {
                                    'filtered': {
                                        'filter': {
                                            'term': {
                                                'foo': 'baz'
                                            }
                                        }
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }

        assert build_or_query('foo', ['bar', 'baz']) == expected

    def test_build_exact_query(self):
        mapping = {'foo': ['bar', 'baz']}
        expected = {
            'query': {
                'filtered': {
                    'filter': {
                        'and': [
                            {
                                'query': {
                                    'filtered': {
                                        'filter': {
                                            'or': [
                                                {
                                                    'query': {
                                                        'filtered': {
                                                            'filter': {
                                                                'term': {
                                                                    'foo': 'bar'
                                                                }
                                                            }
                                                        }
                                                    }
                                                },
                                                {
                                                    'query': {
                                                        'filtered': {
                                                            'filter': {
                                                                'term': {
                                                                    'foo': 'baz'
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }

        assert build_exact_query(mapping, 'records', 'record') == expected
