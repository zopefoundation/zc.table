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

$Id: table.py 4428 2005-12-13 23:35:48Z gary $
"""
from xml.sax.saxutils import quoteattr

from zope import interface, component
import zope.cachedescriptors.property

from zc.table import interfaces
import zc.resourcelibrary

class Formatter(object):
    interface.implements(interfaces.IFormatter)
    items = None

    def __init__(self, context, request, items, visible_column_names=None,
                 batch_start=None, batch_size=None, prefix=None, columns=None):
        self.context = context
        self.request = request
        self.annotations = {}
        self.setItems(items)
        if columns is None:
            assert self.columns is not None
        else:
            self.columns = columns
        if not visible_column_names:
            self.visible_columns = self.columns
        else:
            self.visible_columns = [
                self.columns_by_name[nm] for nm in visible_column_names]
        self.batch_start = batch_start
        self.batch_size = batch_size
        self.prefix = prefix
        self.cssClasses = {}

    def setItems(self, items):
        self.items = items

    @zope.cachedescriptors.property.Lazy
    def columns_by_name(self):
        res = {}
        for col in self.columns:
            assert col.name not in res
            res[col.name] = col
        return res

    def _getCSSClass(self, element):
        klass = self.cssClasses.get(element)
        return klass and ' class=%s' % quoteattr(klass) or ''

    def __call__(self):
        return '\n<table%s>\n%s</table>\n%s' % (
                self._getCSSClass('table'), self.renderContents(),
                self.renderExtra())

    def renderExtra(self):
        zc.resourcelibrary.need('zc.table')
        return ''

    def renderContents(self):
        return '  <thead%s>\n%s  </thead>\n  <tbody>\n%s  </tbody>\n' % (
                self._getCSSClass('thead'), self.renderHeaderRow(),
                self.renderRows())

    def renderHeaderRow(self):
        return '    <tr%s>\n%s    </tr>\n' %(
            self._getCSSClass('tr'), self.renderHeaders())

    def renderHeaders(self):
        return ''.join(
            [self.renderHeader(col) for col in self.visible_columns])

    def renderHeader(self, column):
        return '      <th%s>\n        %s\n      </th>\n' % (
            self._getCSSClass('th'), self.getHeader(column))

    def getHeaders(self):
        return [self.getHeader(column) for column in self.visible_columns]

    def getHeader(self, column):
        return column.renderHeader(self)

    def renderRows(self):
        return ''.join([self.renderRow(item) for item in self.getItems()])

    def getRows(self):
        for item in self.getItems():
            yield [column.renderCell(item, self)
                   for column in self.visible_columns]

    def renderRow(self, item):
        return '  <tr%s>\n%s  </tr>\n' % (
            self._getCSSClass('tr'), self.renderCells(item))

    def renderCells(self, item):
        return ''.join(
            [self.renderCell(item, col) for col in self.visible_columns])

    def renderCell(self, item, column):
        return '    <td%s>\n      %s\n    </td>\n' % (
            self._getCSSClass('td'), self.getCell(item, column),)

    def getCells(self, item):
        return [self.getCell(item, column) for column in self.visible_columns]

    def getCell(self, item, column):
        return column.renderCell(item, self)

    def getItems(self):
        batch_start = self.batch_start or 0
        batch_size = self.batch_size or 0
        if not self.batch_size:
            if not batch_start: # ok, no work to be done.
                for i in self.items:
                    yield i
                raise StopIteration
            batch_end = None
        else:
            batch_end = batch_start + batch_size
        try:
            for i in self.items[batch_start:batch_end]:
                yield i
        except (AttributeError, TypeError):
            for i, item in enumerate(self.items):
                if batch_end is not None and i >= batch_end:
                    return
                if i >= batch_start:
                    yield item

# sorting helpers

class ColumnSortedItems(object):
    # not intended to be persistent!
    """a wrapper for items that sorts lazily based on ISortableColumns.

    Given items, a list of (column name, reversed boolean) pairs beginning
    with the primary sort column, and the formatter, supports iteration, len,
    and __getitem__ access including slices.
    """
    interface.implements(interfaces.IColumnSortedItems)

    formatter = None

    def __init__(self, items, sort_on):
        self._items = items
        self.sort_on = sort_on # tuple of (column name, reversed) pairs
        self._cache = []
        self._iterable = None

    @property
    def items(self):
        if getattr(self._items, '__getitem__', None) is not None:
            return self._items
        else:
            return self._iter()

    def _iter(self):
        # this design is intended to handle multiple simultaneous iterations
        ix = 0
        cache = self._cache
        iterable = self._iterable
        if iterable is None:
            iterable = self._iterable = iter(self._items)
        while True:
            try:
                yield cache[ix]
            except IndexError:
                next = iterable.next() # let StopIteration fall through
                cache.append(next)
                yield next
            ix += 1

    def setFormatter(self, formatter):
        self.formatter = formatter

    @property
    def sorters(self):
        res = []
        for nm, reversed in self.sort_on:
            column = self.formatter.columns_by_name[nm]
            if reversed:
                res.append(column.reversesort)
            else:
                res.append(column.sort)
        return res

    def __getitem__(self, key):
        if isinstance(key, slice):
            start = slice.start
            stop = slice.stop
            stride = slice.step
        else:
            start = stop = key
            stride = 1

        items = self.items
        if not self.sort_on:
            try:
                return items.__getitem__(key)
            except (AttributeError, TypeError):
                if stride != 1:
                    raise NotImplemented
                res = []
                for ix, val in enumerate(items):
                    if ix >= start:
                        res.append(val)
                    if ix >= stop:
                        break

                if isinstance(key, slice):
                    return res
                elif res:
                    return res[0]
                else:
                    raise IndexError, 'list index out of range'

        items = self.sorters[0](
            items, self.formatter, start, stop, self.sorters[1:])

        if isinstance(key, slice):
            return items[start:stop:stride]
        else:
            return items[key]

    def __nonzero__(self):
        try:
            iter(self.items).next()
        except StopIteration:
            return False
        return True

    def __iter__(self):
        if not self.sort_on:
            return iter(self.items)
        else:
            sorters = self.sorters
            return iter(sorters[0](
                self.items, self.formatter, 0, None, sorters[1:]))

    def __len__(self):
        return len(self.items)

def getRequestSortOn(request, sort_on_name):
    """get the sorting values from the request.

    Returns a list of (name, reversed) pairs.
    """
    # useful for code that wants to get the sort on values themselves
    sort_on = None
    sorting = request.form.get(sort_on_name)
    if sorting:
        offset = 0
        res = {}
        for ix, name in enumerate(sorting):
            val = res.get(name)
            if val is None:
                res[name] = [ix + offset, name, False]
            else:
                val[0] = ix + offset
                val[2] = not val[2]
        if res:
            res = res.values()
            res.sort()
            res.reverse()
            sort_on = [[nm, reverse] for ix, nm, reverse in res]
    return sort_on

def getMungedSortOn(request, sort_on_name, sort_on):
    """get the sorting values from the request.

    optionally begins with sort_on values.  Returns a list of (name, reversed)
    pairs.
    """
    res = getRequestSortOn(request, sort_on_name)
    if res is None:
        res = sort_on
    elif sort_on:
        for nm, reverse in sort_on:
            for ix, (res_nm, res_reverse) in enumerate(res):
                if nm == res_nm:
                    res[ix][1] = not (res_reverse ^ reverse)
                    break
            else:
                res.append([nm, reverse])
    return res

def getSortOnName(prefix=None):
    """convert the table prefix to the 'sort on' name used in forms"""
    # useful for code that wants to get the sort on values themselves
    sort_on_name = 'sort_on'
    if prefix is not None:
        if not prefix.endswith('.'):
            prefix += '.'
        sort_on_name = prefix + sort_on_name
    return sort_on_name


class SortingFormatterMixin(object):
    """automatically munges sort_on values with sort settings in the request.
    """

    def __init__(self, context, request, items, visible_column_names=None,
                 batch_start=None, batch_size=None, prefix=None, columns=None,
                 sort_on=None, ignore_request=False):
        if not ignore_request:
            sort_on = getMungedSortOn(request, getSortOnName(prefix), sort_on)
        else:
            sort_on = sort_on
        if sort_on or getattr(items, '__getitem__', None) is None:
            items = ColumnSortedItems(items, sort_on)

        super(SortingFormatterMixin, self).__init__(
            context, request, items, visible_column_names,
            batch_start, batch_size, prefix, columns)

        if sort_on:
            items.setFormatter(self)

    def setItems(self, items):
        if (interfaces.IColumnSortedItems.providedBy(self.items) and
            not interfaces.IColumnSortedItems.providedBy(items)):
            items = ColumnSortedItems(items, self.items.sort_on)
        if interfaces.IColumnSortedItems.providedBy(items):
            items.setFormatter(self)
        self.items = items

class AbstractSortFormatterMixin(object):
    """provides sorting UI: concrete classes must declare script_name."""

    script_name = None # Must be defined in subclass

    def getHeader(self, column):
        contents = column.renderHeader(self)
        if (interfaces.ISortableColumn.providedBy(column)):
            contents = self._addSortUi(contents, column)
        return contents

    def _addSortUi(self, header, column):
        columnName = column.name
        resource_path = component.getAdapter(self.request, name='zc.table')()
        if (interfaces.IColumnSortedItems.providedBy(self.items) and
            self.items.sort_on):
            sortColumnName, sortReversed = self.items.sort_on[0]
        else:
            sortColumnName = sortReversed = None
        if columnName == sortColumnName:
            if sortReversed:
                dirIndicator = ('<img src="%s/sort_arrows_up.gif" '
                                'class="sort-indicator" '
                                'alt="(ascending)"/>' % resource_path)
            else:
                dirIndicator = ('<img src="%s/sort_arrows_down.gif" '
                                'class="sort-indicator" '
                                'alt="(descending)"/>' % resource_path)
        else:
            dirIndicator = ('<img src="%s/sort_arrows.gif" '
                            'class="sort-indicator" '
                            'alt="(sortable)"/>' % resource_path)
        sort_on_name = getSortOnName(self.prefix)
        script_name = self.script_name
        return self._header_template(locals())

    def _header_template(self, options):
        # The <img> below is intentionally not in the <span> because IE
        # doesn't underline it correctly when the CSS class is changed.
        # XXX can we avoid changing the className and get a similar effect?
        template = """
            <span class="zc-table-sortable"
                  onclick="javascript: %(script_name)s(
                        '%(columnName)s', '%(sort_on_name)s')"
                    onMouseOver="javascript: this.className='sortable zc-table-sortable'"
                    onMouseOut="javascript: this.className='zc-table-sortable'">
                %(header)s</span> %(dirIndicator)s
        """
        return template % options

class StandaloneSortFormatterMixin(AbstractSortFormatterMixin):
    "A version of the sort formatter mixin for standalone tables, not forms"

    script_name = 'onSortClickStandalone'


class FormSortFormatterMixin(AbstractSortFormatterMixin):
    """A version of the sort formatter mixin that plays well within forms.
    Does *not* draw a form tag itself, and requires something else to do so.
    """

    def __init__(self, context, request, items, visible_column_names=None,
                 batch_start=None, batch_size=None, prefix=None, columns=None,
                 sort_on=None, ignore_request=False):
        if not ignore_request:
            sort_on = (
                getRequestSortOn(request, getSortOnName(prefix)) or sort_on)
        else:
            sort_on = sort_on
        if sort_on or getattr(items, '__getitem__', None) is None:
            items = ColumnSortedItems(items, sort_on)

        super(FormSortFormatterMixin, self).__init__(
            context, request, items, visible_column_names,
            batch_start, batch_size, prefix, columns)

        if sort_on:
            items.setFormatter(self)

    script_name = 'onSortClickForm'

    def renderExtra(self):
        """Render the hidden input field used to keep up with sorting"""
        if (interfaces.IColumnSortedItems.providedBy(self.items) and
            self.items.sort_on):
            value = []
            for name, reverse in reversed(self.items.sort_on):
                value.append(name)
                if reverse:
                    value.append(name)
            value = ' '.join(value)
        else:
            value = ''

        sort_on_name = getSortOnName(self.prefix)
        return '<input type="hidden" name=%s id=%s value=%s />\n' % (
            quoteattr(sort_on_name+":tokens"),
            quoteattr(sort_on_name),
            quoteattr(value)
            ) + super(FormSortFormatterMixin, self).renderExtra()

    def setItems(self, items):
        if (interfaces.IColumnSortedItems.providedBy(self.items) and
            not interfaces.IColumnSortedItems.providedBy(items)):
            items = ColumnSortedItems(items, self.items.sort_on)
        if interfaces.IColumnSortedItems.providedBy(items):
            items.setFormatter(self)
        self.items = items

class AlternatingRowFormatterMixin(object):
    row_classes = ('even', 'odd')

    def renderRows(self):
        self.row = 0
        return super(AlternatingRowFormatterMixin, self).renderRows()

    def renderRow(self, item):
        self.row += 1
        klass = self.cssClasses.get('tr', '')
        if klass:
            klass += ' '
        return '  <tr class=%s>\n%s  </tr>\n' % (
            quoteattr(klass + self.row_classes[self.row % 2]),
            self.renderCells(item))


# TODO Remove all these concrete classes

class SortingFormatter(SortingFormatterMixin, Formatter):
    pass

class AlternatingRowFormatter(AlternatingRowFormatterMixin, Formatter):
    pass

class StandaloneSortFormatter(
    SortingFormatterMixin, StandaloneSortFormatterMixin, Formatter):
    pass

class FormSortFormatter(FormSortFormatterMixin, Formatter):
    pass

class StandaloneFullFormatter(
    SortingFormatterMixin, StandaloneSortFormatterMixin,
    AlternatingRowFormatterMixin, Formatter):
    pass

class FormFullFormatter(
    FormSortFormatterMixin, AlternatingRowFormatterMixin, Formatter):
    pass
