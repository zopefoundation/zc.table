##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""
from zope import interface
from zope.app import pagetemplate

import zc.table.table
import zc.table.interfaces

unspecified = object()

class Formatter(zc.table.table.FormSortFormatterMixin,
                zc.table.table.AlternatingRowFormatterMixin,
                zc.table.table.Formatter):
    interface.classProvides(zc.table.interfaces.IFormatterFactory)

    def __init__(self, context, request, items, visible_column_names=None,
                 batch_start=None, batch_size=unspecified, prefix=None,
                 columns=None, sort_on=None):
        if batch_size is unspecified:
            batch_size = 20

        if prefix is None:
            prefix = 'zc.table'

        super(Formatter, self).__init__(
            context, request, items, visible_column_names,
            batch_start, batch_size, prefix, columns,
            sort_on=sort_on,
            )

    @property
    def batch_change_name(self):
        return self.prefix + '.batch_change'

    @property
    def batch_start_name(self):
        return self.prefix + '.batch_start'

    _batch_start = None
    _batch_start_computed = False

    def setPrefix(self, prefix):
        super(Formatter, self).setPrefix(prefix)
        self._batch_start_computed = False

    @apply
    def batch_start():
        def fget(self):
            if not self._batch_start_computed:
                self.updateBatching()
            return self._batch_start
        def fset(self, value):
            self._batch_start = value
            self._batch_start_computed = False
        def fdel(self):
            self._batch_start = None
        return property(fget, fset, fdel)

    def updateBatching(self):
        request = self.request
        if self._batch_start is None:
            try:
                self.batch_start = int(request.get(self.batch_start_name, '0'))
            except ValueError:
                self._batch_start = 0
        # Handle requests to change batches:
        change = request.get(self.batch_change_name)
        if change == "next":
            self._batch_start += self.batch_size
            try:
                length = len(self.items)
            except TypeError:
                for length, ob in enumerate(self.items):
                    if length > self._batch_start:
                        break
                else:
                    self._batch_start = length
            else:
                if self._batch_start > length:
                    self._batch_start = length
        elif change == "back":
            self._batch_start -= self.batch_size
            if self._batch_start < 0:
                self._batch_start = 0

        self.next_batch_start = self._batch_start + self.batch_size
        try:
            self.items[self.next_batch_start]
        except IndexError:
            self.next_batch_start = None

        self.previous_batch_start = self._batch_start - self.batch_size
        if self.previous_batch_start < 0:
            self.previous_batch_start = None
        self._batch_start_computed = True

    batching_template = pagetemplate.ViewPageTemplateFile('batching.pt')
    def renderExtra(self):
        if not self._batch_start_computed:
            self.updateBatching()
        return self.batching_template() + super(Formatter, self).renderExtra()

    def __call__(self):
        return ('\n'
                '<div style="width: 100%"> '
                '<!-- this div is a workaround for an IE bug -->\n'
                '<table class="listingdescription" style="width:100%" '
                + ('name="%s">\n' % self.prefix)
                + self.renderContents() +
                '</table>\n'
                + self.renderExtra() +
                '</div> <!-- end IE bug workaround -->\n'
               )
