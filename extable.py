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
"""Table formatting and configuration

$Id$
"""
from zc.table import table
from xml.sax.saxutils import quoteattr

class SelectedItemFormatterMixin(table.AlternatingRowFormatterMixin,
                                 table.Formatter):
    """A formatter that allows selecting a single item."""

    # Simply set the item that is being selected
    selectedItem = None

    def renderRow(self, item):
        self.row += 1
        klass = self.cssClasses.get('tr', '')
        if klass:
            klass += ' '
        else:
            klass += self.row_classes[self.row % 2]

        if item == self.selectedItem:
            klass += ' selected'

        return '  <tr class=%s>\n%s  </tr>\n' % (
            quoteattr(klass), self.renderCells(item))


class CSSColumnFormatterMixin(object):
    """A formatter that allows you to specify a CSS class per column."""

    columnCSS = None

    def __init__(self, *args, **kw):
        super(CSSColumnFormatterMixin, self).__init__(*args, **kw)
        self.columnCSS = {}

    def renderHeader(self, column):
        klass = self.cssClasses.get('tr', '')
        if column.name in self.columnCSS:
            klass += klass and ' ' or '' + self.columnCSS[column.name]
        return '      <th class=%s>\n        %s\n      </th>\n' % (
            quoteattr(klass), self.getHeader(column))

    def renderCell(self, item, column):
        klass = self.cssClasses.get('tr', '')
        if column.name in self.columnCSS:
            klass += klass and ' ' or '' + self.columnCSS[column.name]
        return '    <td class=%s>\n      %s\n    </td>\n' % (
            quoteattr(klass), self.getCell(item, column))


class WidthSpecificationFormatterMixin(object):
    """A formatter that allows specifying the width of each column."""

    # If set, this is expected to be a sequence of width integers
    columnWidths = None

    def renderHeader(self, column):
        width = ''
        if self.columnWidths:
            idx = list(self.visible_columns).index(column)
            width = ' width="%i"' %self.columnWidths[idx]

        return '      <th%s%s>\n        %s\n      </th>\n' % (
            self._getCSSClass('th'), width, self.getHeader(column))


