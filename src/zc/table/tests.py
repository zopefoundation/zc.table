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
import doctest
import unittest

import zope.formlib.widgets
import zope.publisher.interfaces.browser
import zope.schema.interfaces
from zope import component
from zope.component.testing import setUp
from zope.component.testing import tearDown


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


DOCTEST_FLAGS = (doctest.NORMALIZE_WHITESPACE |
                 doctest.ELLIPSIS |
                 doctest.IGNORE_EXCEPTION_DETAIL)


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'README.rst',
            optionflags=DOCTEST_FLAGS,
        ),
        doctest.DocFileSuite(
            'column.rst',
            setUp=columnSetUp, tearDown=tearDown,
            optionflags=DOCTEST_FLAGS,
        ),
        doctest.DocFileSuite(
            'fieldcolumn.rst',
            setUp=fieldColumnSetUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
        ),
    ))
