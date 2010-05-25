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
"""Useful predefined columns

$Id: column.py 4318 2005-12-06 03:41:37Z gary $
"""
import warnings
from xml.sax.saxutils import quoteattr

from zope import interface, component, schema, i18n
from zope.app.form.interfaces import IInputWidget
from zope.app.form.interfaces import WidgetInputError, WidgetsError

from zc.table import interfaces

class Column(object):
    interface.implements(interfaces.IColumn)
    title = None
    name = None

    def __init__(self, title=None, name=None):
        if title is not None:
            self.title = title

        self.name = name or title

    def renderHeader(self, formatter):
        return i18n.translate(
            self.title, context=formatter.request, default=self.title)

    def renderCell(self, item, formatter):
        raise NotImplementedError('Subclasses must provide their '
                                  'own renderCell method.')

class SortingColumn(Column):
    interface.implements(interfaces.ISortableColumn)

    # sort and reversesort are part of ISortableColumn, not IColumn, but are
    # put here to provide a reasonable default implementation.

    def __init__(self, title=None, name=None, subsort=False):
        self.subsort = subsort
        super(SortingColumn, self).__init__(title, name)

    def _sort(self, items, formatter, start, stop, sorters, multiplier):
        if self.subsort and sorters:
            items = sorters[0](items, formatter, start, stop, sorters[1:])
        else:
            items = list(items) # don't mutate original
        getSortKey = self.getSortKey

        items.sort(
            cmp=lambda a, b: multiplier*cmp(a, b),
            key=lambda item: getSortKey(item, formatter))

        return items

    def sort(self, items, formatter, start, stop, sorters):
        return self._sort(items, formatter, start, stop, sorters, 1)

    def reversesort(self, items, formatter, start, stop, sorters):
        return self._sort(items, formatter, start, stop, sorters, -1)

    # this is a convenience to override if you just want to keep the basic
    # implementation but change the comparison values.

    def getSortKey(self, item, formatter):
        raise NotImplementedError

class GetterColumn(SortingColumn):
    """Column for simple use cases.

    title - the title of the column
    getter - a callable that is passed the item and the table formatter;
        returns the value used in the cell
    cell_formatter - a callable that is passed the result of getter, the
        item, and the table formatter; returns the formatted HTML
    """
    interface.implementsOnly(interfaces.IColumn)

    def __init__(self, title=None, getter=None, cell_formatter=None, 
                 name=None, subsort=False):
        if getter is not None:
            self.getter = getter

        if cell_formatter is not None:
            self.cell_formatter = cell_formatter

        super(GetterColumn, self).__init__(title, name, subsort=subsort)

    def getter(self, item, formatter):
        return item

    def cell_formatter(self, value, item, formatter):
        return unicode(value).replace('&', '&#38;') \
                              .replace('<', '&#60;') \
                              .replace('>', '&#62;')

    def renderCell(self, item, formatter):
        value = self.getter(item, formatter)
        return self.cell_formatter(value, item, formatter)

    # this is a convenience to override if you just want to keep the basic
    # implementation but change the comparison values.

    def getSortKey(self, item, formatter):
        return self.getter(item, formatter)


class MailtoColumn(GetterColumn):
    def renderCell(self, item, formatter):
        email = super(MailtoColumn, self).renderCell(item, formatter)
        return '<a href="mailto:%s">%s</a>' % (email, email)

class FieldEditColumn(Column):
    """Columns that supports field/widget update

    Note that fields are only bound if bind == True.
    """

    def __init__(self, title=None, prefix=None, field=None,
                 idgetter=None, getter=None, setter=None, name='', bind=False, 
                 widget_class=None, widget_extra=None):
        super(FieldEditColumn, self).__init__(title, name)
        assert prefix is not None # this is required
        assert field is not None # this is required
        assert idgetter is not None # this is required
        self.prefix = prefix
        self.field = field
        self.idgetter = idgetter
        if getter is None:
            getter = field.get
        self.get = getter
        if setter is None:
            setter = field.set
        self.set = setter
        self.bind = bind
        self.widget_class = widget_class
        self.widget_extra = widget_extra

    def makeId(self, item):
        return ''.join(self.idgetter(item).encode('base64').split())

    def input(self, items, request):
        if not hasattr(request, 'form'):
            warnings.warn(
                'input should be called with a request, not a formatter',
                DeprecationWarning, 2)
            request = request.request
        data = {}
        errors = []
        bind = self.bind
        if not bind:
            widget = component.getMultiAdapter(
                (self.field, request), IInputWidget)
        for item in items:
            if bind:
                widget = component.getMultiAdapter(
                    (self.field.bind(item), request), IInputWidget)
            id = self.makeId(item)
            # this is wrong: should use formatter prefix.  column should not
            # have a prefix.  This requires a rewrite; this entire class
            # will be deprecated.
            widget.setPrefix(self.prefix + '.' + id)
            if widget.hasInput():
                try:
                    data[id] = widget.getInputValue()
                except WidgetInputError, v:
                    errors.append(v)

        if errors:
            raise WidgetsError(errors)
        return data

    def update(self, items, data):
        changed = False
        for item in items:
            id = self.makeId(item)
            v = data.get(id, self)
            if v is self:
                continue
            if self.get(item) != v:
                self.set(item, v)
                changed = True
        return changed

    def renderCell(self, item, formatter):
        id = self.makeId(item)
        request = formatter.request
        field = self.field
        if self.bind:
            field = field.bind(item)
        widget = component.getMultiAdapter((field, request), IInputWidget)
        widget.setPrefix(self.prefix + '.' + id)
        if self.widget_extra is not None:
            widget.extra = self.widget_extra
        if self.widget_class is not None:
            widget.cssClass = self.widget_class
        ignoreStickyValues = getattr(formatter, 'ignoreStickyValues', False)
        if ignoreStickyValues or not widget.hasInput():
            widget.setRenderedValue(self.get(item))
        return widget()


class SelectionColumn(FieldEditColumn):
    title = ''

    def __init__(self, idgetter, field=None, prefix=None, getter=None,
                 setter=None, title=None, name='', hide_header=False):
        if field is None:
            field = schema.Bool()
        if not prefix:
            if field.__name__:
                prefix = field.__name__ + '_selection_column'
            else:
                prefix = 'selection_column'
        if getter is None:
            getter = lambda item: False
        if setter is None:
            setter = lambda item, value: None
        if title is None:
            title = field.title or ""
        self.hide_header = hide_header
        super(SelectionColumn, self).__init__(field=field, prefix=prefix,
                                              getter=getter, setter=setter,
                                              idgetter=idgetter, title=title,
                                              name=name)

    def renderHeader(self, formatter):
        if self.hide_header:
            return ''
        return super(SelectionColumn, self).renderHeader(formatter)

    def getSelected(self, items, request):
        """Return the items which were selected."""
        data = self.input(items, request)
        return [item for item in items if data.get(self.makeId(item))]

class SubmitColumn(Column):
    def __init__(self, title=None, prefix=None, idgetter=None, action=None,
                 labelgetter=None, condition=None,
                 extra=None, cssClass=None, renderer=None, name=''):
        super(SubmitColumn, self).__init__(title, name)
        # hacked together. :-/
        assert prefix is not None # this is required
        assert idgetter is not None # this is required
        assert labelgetter is not None # this is required
        assert action is not None # this is required
        self.prefix = prefix
        self.idgetter = idgetter
        self.action = action
        self.renderer=renderer
        self.condition = condition
        self.extra = extra
        self.cssClass = cssClass
        self.labelgetter = labelgetter

    def makeId(self, item):
        return ''.join(self.idgetter(item).encode('base64').split())

    def input(self, items, request):
        for item in items:
            id = self.makeId(item)
            identifier = '%s.%s' % (self.prefix, id)
            if identifier in request.form:
                if self.condition is None or self.condition(item):
                    return id
                break

    def update(self, items, data):
        if data:
            for item in items:
                id = self.makeId(item)
                if id == data:
                    self.action(item)
                    return True
        return False

    def renderCell(self, item, formatter):
        if self.condition is None or self.condition(item):
            id = self.makeId(item)
            identifier = '%s.%s' % (self.prefix, id)
            if self.renderer is not None:
                return self.renderer(
                    item, identifier, formatter, self.extra, self.cssClass)
            label = self.labelgetter(item, formatter)
            label = i18n.translate(
                label, context=formatter.request, default=label)
            val = "<input type='submit' name=%s value=%s %s" % (
                quoteattr(identifier),
                quoteattr(label),
                self.extra and quoteattr(self.extra) or '')
            if self.cssClass:
                val = "%s class=%s />" % (val, quoteattr(self.cssClass))
            else:
                val += " />"
            return val
        return ''
