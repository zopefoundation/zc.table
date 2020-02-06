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
import doctest
import re
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


# Strip out u'' literals in doctests, adapted from
# <https://stackoverflow.com/a/56507895>.
class Py23OutputChecker(doctest.OutputChecker, object):

    RE = re.compile(r"(\W|^)[uU]([rR]?[\'\"])", re.UNICODE)

    def remove_u(self, want, got):
        return (re.sub(self.RE, r'\1\2', want),
                re.sub(self.RE, r'\1\2', got))

    def check_output(self, want, got, optionflags):
        want, got = self.remove_u(want, got)
        return super(Py23OutputChecker, self).check_output(
            want, got, optionflags)

    def output_difference(self, example, got, optionflags):
        example.want, got = self.remove_u(example.want, got)
        return super(Py23OutputChecker, self).output_difference(
            example, got, optionflags)


DOCTEST_FLAGS = (doctest.NORMALIZE_WHITESPACE |
                 doctest.ELLIPSIS |
                 doctest.IGNORE_EXCEPTION_DETAIL)


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'README.rst',
            optionflags=DOCTEST_FLAGS,
            checker=Py23OutputChecker(),
        ),
        doctest.DocFileSuite(
            'column.rst',
            setUp=columnSetUp, tearDown=tearDown,
            optionflags=DOCTEST_FLAGS,
            checker=Py23OutputChecker(),
        ),
        doctest.DocFileSuite(
            'fieldcolumn.rst',
            setUp=fieldColumnSetUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
            checker=Py23OutputChecker(),
        ),
    ))
