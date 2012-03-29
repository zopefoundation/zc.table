##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
from zope.component.testing import setUp, tearDown
import zope.publisher.interfaces.browser
import zope.schema.interfaces
import zope.formlib.widgets


def columnSetUp(test):
    setUp(test)
    component.provideAdapter(
        zope.formlib.widgets.TextWidget,
        (zope.schema.interfaces.ITextLine,
         zope.publisher.interfaces.browser.IBrowserRequest,
         ),
        zope.formlib.interfaces.IInputWidget)
    component.provideAdapter(
        zope.formlib.widgets.CheckBoxWidget,
        (zope.schema.interfaces.IBool,
         zope.publisher.interfaces.browser.IBrowserRequest,
         ),
        zope.formlib.interfaces.IInputWidget)


def fieldColumnSetUp(test):
    columnSetUp(test)
    component.provideAdapter(
        zope.formlib.widgets.ChoiceDisplayWidget,
        (zope.schema.interfaces.IChoice,
         zope.publisher.interfaces.browser.IBrowserRequest),
        zope.formlib.interfaces.IDisplayWidget)
    component.provideAdapter(
        zope.formlib.widgets.ChoiceInputWidget,
        (zope.schema.interfaces.IChoice,
         zope.publisher.interfaces.browser.IBrowserRequest),
        zope.formlib.interfaces.IInputWidget)
    component.provideAdapter(
        zope.formlib.widgets.DropdownWidget,
        (zope.schema.interfaces.IChoice,
         zope.schema.interfaces.IVocabularyTokenized,
         zope.publisher.interfaces.browser.IBrowserRequest),
        zope.formlib.interfaces.IInputWidget)
    component.provideAdapter(
        zope.formlib.widgets.ChoiceDisplayWidget,
        (zope.schema.interfaces.IChoice,
         zope.schema.interfaces.IVocabularyTokenized,
         zope.publisher.interfaces.browser.IBrowserRequest),
        zope.formlib.interfaces.IDisplayWidget)


def test_suite():
    import doctest
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
            optionflags=doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS,
            ),
        doctest.DocFileSuite(
            'column.txt',
            setUp=columnSetUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS,
            ),
        doctest.DocFileSuite(
            'fieldcolumn.txt',
            setUp=fieldColumnSetUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS,
            ),
        ))
