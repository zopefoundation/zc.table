##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Testing helpers

$Id: testing.py 2520 2005-06-27 21:26:18Z benji $
"""
from zope import interface, component
from zope.app.testing import ztapi
import zc.table.interfaces
import zc.table.table


class SimpleFormatter(zc.table.table.Formatter):
    interface.classProvides(zc.table.interfaces.IFormatterFactory)


def setUp(test):
    ztapi.provideUtility(zc.table.interfaces.IFormatterFactory, 
                         SimpleFormatter)
    assert component.getUtility(zc.table.interfaces.IFormatterFactory) != None
    

def tearDown(test):
    ztapi.unprovideUtility(zc.table.interfaces.IFormatterFactory)
