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
"""table package interfaces

$Id: interfaces.py 4318 2005-12-06 03:41:37Z gary $
"""
import re

from zope import interface
from zope import schema


pythonLikeNameConstraint = re.compile(r'^[a-zA-Z_]\w*$').match


class IColumn(interface.Interface):

    name = schema.BytesLine(
        title='Name',
        description=('Name used for column in options of a table '
                     'configuration.  Must be unique within any set of '
                     'columns passed to a table formatter.'),
        constraint=pythonLikeNameConstraint,
    )

    title = schema.TextLine(
        title='Title',
        description='The title of the column, used in configuration dialogs.',
    )

    def renderHeader(formatter):
        """Renders a table header.

        'formatter' - The IFormatter that is using the IColumn.

        Returns html_fragment, not including any surrounding <th> tags.
        """

    def renderCell(item, formatter):
        """Renders a table cell.

        'item' - the object on this row.
        'formatter' - The IFormatter that is using the IColumn.

        Returns html_fragment, not including any surrounding <td> tags.
        """


class ISortableColumn(interface.Interface):

    def sort(items, formatter, start, stop, sorters):
        """Return a list of items in sorted order.

        Formatter is passed to aid calculation of sort parameters.  Start and
        stop are passed in order to provide a hint as to the range needed, if
        the algorithm can optimize.  Sorters are a list of zero or more
        sub-sort callables with the same signature which may be used if
        desired to sub-sort values with equivalent sort values according
        to this column.

        The original items sequence should not be mutated."""

    def reversesort(items, formatter, start, stop, sorters):
        """Return a list of items in reverse sorted order.

        Formatter is passed to aid calculation of sort parameters.  Start and
        stop are passed in order to provide a hint as to the range needed, if
        the algorithm can optimize.  Sorters are a list of zero or more
        sub-sort callables with the same signature as this method, which may
        be used if desired to sub-sort values with equivalent sort values
        according to this column.

        The original items sequence should not be mutated."""


class IColumnSortedItems(interface.Interface):
    """items that support sorting by column.  setFormatter must be called
    with the formatter to be used before methods work.  This is typically done
    in a formatter's __init__"""

    sort_on = interface.Attribute(
        """list of (colmun name, reversed boolean) beginning with the primary
        sort column.""")

    def __getitem__(key):
        """given index or slice, returns requested item(s) based on sort order.
        """

    def __iter__():
        """iterates over items in sort order"""

    def __len__():
        """returns len of sorted items"""

    def setFormatter(formatter):
        "tell the items about the formatter before using any of the methods"


class IFormatter(interface.Interface):

    annotations = schema.Dict(
        title="Annotations",
        description='Stores arbitrary application data under '
        'package-unique keys. '
        'By "package-unique keys", we mean keys that are are unique by '
        'virtue of including the dotted name of a package as a prefix. '
        'A package name is used to limit the authority for picking names '
        'for a package to the people using that package. '
        'For example, when implementing annotations for a zc.foo package, '
        'the key would be (or at least begin with) the following::'
        ''
        ' "zc.foo"')

    request = schema.Field(
        title='Request',
        description='The request object.',
    )

    context = schema.Field(
        title='Context',
        description='The (Zope ILocation) context for which the table '
        'formatter is rendering')

    items = schema.List(
        title='Items',
        description='The items that will be rendered by __call__.  items '
        'preferably support a way to get a slice (__getitem__ or the '
        'deprecated getslice) or alternatively may merely be iterable.  '
        'see getItems.')

    columns = schema.Tuple(
        title='All the columns that make up this table.',
        description='All columns that may ever be a visible column.  A non-'
        'visible column may still have an effect on operations such as '
        'sorting.  The names of all columns must be unique within the '
        'sequence.',
        unique=True,
    )

    visible_columns = schema.Tuple(
        title='The visible columns that make up this table.',
        description='The columns to display when rendering this table.',
        unique=True,
    )

    batch_size = schema.Int(
        title='Number of rows per page',
        description='The number of rows to show at a time.  '
                    'Set to 0 for no batching.',
        default=20,
        min=0,
    )

    batch_start = schema.Int(
        title='Batch Start',
        description='The starting index for batching.',
        default=0,
    )

    prefix = schema.BytesLine(
        title='Prefix',
        description='The prefix for all form names',
        constraint=pythonLikeNameConstraint,
    )

    columns_by_name = schema.Dict(
        title='Columns by Name',
        description='A mapping of column name to column object')

    cssClasses = schema.Dict(
        title='CSS Classes',
        description='A mapping from an HTML element to a CSS class',
        key_type=schema.TextLine(title='The HTML element name'),
        value_type=schema.TextLine(title='The CSS class name'))

    def __call__():
        """Render a complete HTML table from self.items."""

    def renderHeaderRow():
        """Render an HTML table header row from the column headers.

        Uses renderHeaders."""

    def renderHeaders():
        """Render the individual HTML headers from the columns.

        Uses renderHeader."""

    def renderHeader(column):
        """Render a header for the given column.

        Uses getHeader."""

    def getHeader(column):
        """Render header contents for the given column.

        Includes appropriate code for enabling ISortableColumn.

        Uses column.renderHeader"""

    def getHeaders():
        """Retrieve a sequence of rendered column header contents.

        Uses getHeader.

        Available for more low-level use of a table; not used by the other
        table code."""

    def renderRows():
        """Render HTML rows for the self.items.

        Uses renderRow and getItems."""

    def getRows():
        """Retrieve a sequence of sequences of rendered cell contents.

        Uses getCells and getItems.

        Available for more low-level use of a table; not used by the other
        table code."""

    def getCells(item):
        """Retrieve a sequence rendered cell contents for the item.

        Uses getCell.

        Available for more low-level use of a table; not used by the other
        table code."""

    def getCell(item, column):
        """Render the cell contents for the item and column."""

    def renderRow(item):
        """Render a row for the given item.

        Uses renderCells."""

    def renderCells(item):
        """Render the cells--the contents of a row--for the given item.

        Uses renderCell."""

    def renderCell(item, column):
        """Render the cell for the item and column.

        Uses getCell."""

    def getItems():
        """Returns the items to be rendered from the full set of self.items.

        Should be based on batch_start and batch_size, if set.
        """


class IFormatterFactory(interface.Interface):
    """When called returns a table formatter.

    Takes the same arguments as zc.table.table.Formatter"""
