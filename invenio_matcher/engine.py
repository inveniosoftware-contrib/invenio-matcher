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

"""Matcher engine dispatcher."""

from flask import current_app

from .errors import NoEngineDefined
from .registry import engines


def exact(**kwargs):
    """Dispatch the exact call to the engine."""
    return _get_engine().exact(**kwargs)


def fuzzy(**kwargs):
    """Dispatch the fuzzy call to the engine."""
    return _get_engine().fuzzy(**kwargs)


def free(**kwargs):
    """Dispatch the free call to the engine."""
    return _get_engine().free(**kwargs)


def queries(**kwargs):
    """Dispatch the queries call to the engine."""
    return _get_engine().queries(**kwargs)


def _get_engine(engine={}):
    """Get the configured engine.

    Abuses the fact that mutable default arguments are captured in the closure
    environment to cache the value of the engine for subsequent calls."""
    if not engine:
        try:
            engine = engines[current_app.config['MATCHER_ENGINE']]
        except KeyError:
            raise NoEngineDefined('Engine not discovered in the registry, or'
                                  ' not defined in MATCHER_ENGINE')

    return engine
