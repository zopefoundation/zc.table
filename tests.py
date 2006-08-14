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
"""

$Id: tests.py 4428 2005-12-13 23:35:48Z gary $
"""
import unittest
from zope import component
from zope.app.testing import placelesssetup
import zope.publisher.interfaces.browser
import zope.schema.interfaces
import zope.app.form.browser

def columnSetUp(test):
    placelesssetup.setUp(test)
    component.provideAdapter(
        zope.app.form.browser.TextWidget,
        (zope.schema.interfaces.ITextLine,
         zope.publisher.interfaces.browser.IBrowserRequest,
         ),
        zope.app.form.interfaces.IInputWidget)
    component.provideAdapter(
        zope.app.form.browser.CheckBoxWidget,
        (zope.schema.interfaces.IBool,
         zope.publisher.interfaces.browser.IBrowserRequest,
         ),
        zope.app.form.interfaces.IInputWidget)

def test_suite():
    from zope.testing import doctest
    return unittest.TestSuite((
        doctest.DocFileSuite('extable.txt',
            optionflags=doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS,
            ),
        doctest.DocFileSuite('README.txt',
            optionflags=doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS,
            ),
        doctest.DocFileSuite(
            'column.txt',
            setUp = columnSetUp, tearDown=placelesssetup.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS,
            ),
        doctest.DocFileSuite(
            'fieldcolumn.txt',
            setUp = columnSetUp, tearDown=placelesssetup.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS,
            ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

