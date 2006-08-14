======
Tables
======

Tables are general purpose UI constructs designed to simplify presenting
tabular information.  A table has a column set which collects columns and
manages configuration data.

We must register a faux resource directory in preparation::

    >>> import zope.interface
    >>> import zope.component
    >>> import zope.publisher.interfaces
    >>> @zope.component.adapter(zope.publisher.interfaces.IRequest)
    ... @zope.interface.implementer(zope.interface.Interface)
    ... def dummyResource(request):
    ...     return lambda:'/@@/zc.table'
    ...
    >>> zope.component.provideAdapter(dummyResource, name='zc.table')

Columns
=======

``Columns`` have methods to render a header and the contents of a cell based on
the item that occupies that cell.  Here's a very simple example::

    >>> from zope import interface
    >>> from zc.table import interfaces
    >>> class GetItemColumn:
    ...     interface.implements(interfaces.IColumn)
    ...     def __init__(self, title, name, attr):
    ...         self.title = title
    ...         self.name = name
    ...         self.attr = attr # This isn't part of IColumn
    ...     def renderHeader(self, formatter):
    ...         return self.title
    ...     def renderCell(self, item, formatter):
    ...         return str(getattr(item, self.attr))

Note that the methods do not provide the <th> and <td> tags.

The title is for display, while the name is for identifying the column within
a collection of columns: a column name must be unique within a collection of
columns used for a table formatter.

`renderHeader` takes a formatter--the table formatter introduced in the section
immediately below this one.  It has the responsibility of rendering the
contents of the header for the column.  `renderCell` takes the item to be
rendered and the formatter, and is responsible for returning the cell contents
for the given item.

The formatter is passed because it contains references to a number of useful
values.  The context and request are particularly important.

Columns may also support sorting by implementing the ISortableColumn interface.
This interface is comprised of two methods, `sort` and `reversesort`.  Both
take the same rather large set of arguments: items, formatter, start, stop,
and sorters.  At least two values should be unsurprising: the `items` are the
items to be sorted, the `formatter` is the table formatter.  The `start` and
`stop` values are the values that are needed for the rendering, so some
implementations may be able to optimize to only give precise results for the
given range.  The `sorters` are optional sub-sorters--callables with signatures
identical to `sort` and `reversesort` that are a further sort refinement that
an implementation may optionally ignore.  If a column has two or
more values that will sort identically, the column might take advantage of any
sub-sorters to further sort the data.

The columns.py file has a number of useful base column classes.  The
columns.txt file discusses some of them.  For our examples here, we will use
the relatively simple and versatile zc.table.column.GetterColumn.  It is
instantiated with two required values and two optional values::

    title - (required) the title of the column.

    getter - (required) a callable that is passed the item and the table
             formatter; returns the value used in the cell.

    cell_formatter - (optional) a callable that is passed the result of getter,
                      the item, and the table formatter; returns the formatted
                      HTML.  defaults to a function that returns the result of
                      trying to convert the result to unicode.

    name - (optional) the name of the column.  The title is used if a name is
           not specified.

It includes a reasonably simple implementation of ISortableColumn but does
not declare the interface itself.  It tries to sort on the basis of the getter
value and can be customized simply by overriding the `getSortKey` method.

Let's import the GetterColumn and create some columns that we'll use later,
and then verify that one of the columns fully implements IColumn.  We'll also
then declare that all three of them provide ISortableColumn and verify one of
them::

    >>> from zc.table.column import GetterColumn
    >>> columns = (
    ...     GetterColumn(u'First', lambda i,f: i.a, subsort=True),
    ...     GetterColumn(u'Second', lambda i,f: i.b, subsort=True),
    ...     GetterColumn(u'Third', lambda i,f: i.c, subsort=True),
    ...     )
    >>> import zope.interface.verify
    >>> zope.interface.verify.verifyObject(interfaces.IColumn, columns[0])
    True
    >>> for c in columns:
    ...     interface.directlyProvides(c, interfaces.ISortableColumn)
    ...
    >>> zope.interface.verify.verifyObject(
    ...     interfaces.ISortableColumn, columns[0])
    True

Formatters
==========

When a sequence of objects are to be turned into an HTML table, a
table.Formatter is used.  The table package includes a simple implementation
of IFormatter as well as a few important variations.

The default Formatter is instantiated with three required arguments--
`context`, `request`, and `items`--and a long string of optional arguments
we'll discuss in a moment.  The first two required arguments are reminiscent
of browser views--and in fact, a table formatter is a specialized browser
view.  The `context` is the object for which the table formatter is being
rendered, and can be important to various columns; and the `request` is the
current request.  The `items` are the full set of items on which the table will
give a view.

The first three optional arguments affect the display::

    visible_column_names=None, batch_start=0, batch_size=0

visible_column_names are a list of column names that should be displayed; note
that even if a column is not visible, it may still affect other behavior such
as sorting, discussed for a couple of Formatter subclasses below.

batch_start is the item position the table should begin to render.  batch_size
is the number of items the table should render; 0 means all.

The next optional argument, `prefix=None`, is particularly important when a
table formatter is used within a form: it sets a prefix for any form fields
and XML identifiers generated for the table or a contained element::

The last optional argument is the full set of columns for the table (not just
the ones curently visible).  It is optional because it may be set instead as
a subclass attribute: the value itself is required on instances.

Lets create some data to format and instantiate the default Formatter.
Our formatters won't need the context, so we'll fake it.  As an
exercise, we'll hide the second column.

    >>> class DataItem:
    ...     def __init__(self, a, b, c):
    ...         self.a = a
    ...         self.b = b
    ...         self.c = c

    >>> items = [DataItem('a0', 'b0', 'c0'),
    ...          DataItem('a2', 'b2', 'c2'),
    ...          DataItem('a1', 'b1', 'c1'),
    ...          ]
    >>> from zc.table import table
    >>> import zope.publisher.browser
    >>> request = zope.publisher.browser.TestRequest()
    >>> context = None
    >>> formatter = table.Formatter(
    ...     context, request, items, visible_column_names=('First', 'Third'),
    ...     columns=columns)
    >>> zope.interface.verify.verifyObject(
    ...     interfaces.IFormatter, formatter)
    True

The simplest way to use a table formatter is to call it, asking the formatter
to render the entire table::

    >>> print formatter()
    <table>
    <thead>
      <tr>
        <th>
          First
        </th>
        <th>
          Third
        </th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>
          a0
        </td>
        <td>
          c0
        </td>
      </tr>
      <tr>
        <td>
          a2
        </td>
        <td>
          c2
        </td>
      </tr>
      <tr>
        <td>
          a1
        </td>
        <td>
          c1
        </td>
      </tr>
    </tbody>
    </table>

If you want more control over the output then you may want to call methods
on the formatter that generate various parts of the output piecemeal.  In
particular, getRows, getHeaders, and getCells exist only for this sort of use.
Here is an example of getRows in use to generate even and odd rows and a
column with cells in a special class:

    >>> html = '<table class="my_class">\n'
    >>> html += '<tr class="header">\n'+ formatter.renderHeaders() + '</tr>\n'
    >>> for index, row in enumerate(formatter.getRows()):
    ...     if index % 2:
    ...         html += '<tr class="even">'
    ...     else:
    ...         html += '<tr class="odd">'
    ...     for index, cell in enumerate(row):
    ...         if index == 0:
    ...             html += '<td class="first_column">'
    ...         else:
    ...             html += '<td>'
    ...         html += cell + '<td>'
    ...     html += '</tr>\n'
    >>> html += '</table>'
    >>> print html
    <table class="my_class">
    <tr class="header">
        <th>
          First
        </th>
        <th>
          Third
        </th>
    </tr>
    <tr class="odd"><td class="first_column">a0<td><td>c0<td></tr>
    <tr class="even"><td class="first_column">a2<td><td>c2<td></tr>
    <tr class="odd"><td class="first_column">a1<td><td>c1<td></tr>
    </table>

However, the formatter provides some simple support for style sheets, since it
is the most common form of customization. Each formatter has an attribute
called ``cssClasses``, which is a mapping from HTML elements to CSS
classes. As you saw above, by default there are no CSS classes registered for
the formatter. Let's now register one for the "table" element:

    >>> formatter.cssClasses['table'] = 'list'
    >>> print formatter()
    <table class="list">
    ...
    </table>

This can be done for every element used in the table. Of course, you can also
unregister the class again:

    >>> del formatter.cssClasses['table']
    >>> print formatter()
    <table>
    ...
    </table>

If you are going to be doing a lot of this sort of thing (or if this approach
is more your style), a subclass of Formatter might be in order--but that
is jumping the gun a bit.  See the section about subclasses below.

Columns are typically defined for a class and reused across requests.
Therefore, they have the request that columns need.  They also have an
`annotations` attribute that allows columns to stash away information that
they need across method calls--for instance, an adapter that every single
cell in a column--and maybe even across multiple columns--will need.

    >>> formatter.annotations
    {}

Batching
========

As discussed above, ``Formatter`` instances can also batch. In order to
batch, `items` must minimally be iterable and ideally support a slice syntax.
batch_size and batch_start, introduced above, are the formatter values to use.
Typically these are passed in on instantiation, but we'll change the attributes
on the existing formatter.

    >>> formatter.batch_size = 1
    >>> print formatter()
    <table>
    <thead>
      <tr>
        <th>
          First
        </th>
        <th>
          Third
        </th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>
          a0
        </td>
        <td>
          c0
        </td>
      </tr>
    </tbody>
    </table>

    >>> formatter.batch_start=1
    >>> print formatter()
    <table>
    <thead>
      <tr>
        <th>
          First
        </th>
        <th>
          Third
        </th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>
          a2
        </td>
        <td>
          c2
        </td>
      </tr>
    </tbody>
    </table>

Fancy Columns
=============

It is easy to make columns be more sophisticated.  For example, if we wanted
a column that held content that was especially wide, we could do this::

    >>> class WideColumn(GetterColumn):
    ...     def renderHeader(self, formatter):
    ...         return '<div style="width:200px">%s</div>' % (
    ...             super(WideColumn, self).renderHeader(formatter),)
    >>> fancy_columns = (
    ...     WideColumn(u'First', lambda i,f: i.a),
    ...     GetterColumn(u'Second', lambda i,f: i.b),
    ...     GetterColumn(u'Third', lambda i,f: i.c),
    ...     )
    >>> formatter = table.Formatter(
    ...     context, request, items, visible_column_names=('First', 'Third'),
    ...     columns=fancy_columns)
    >>> print formatter()
    <table>
    <thead>
      <tr>
        <th>
          <div style="width:200px">First</div>
        </th>
        <th>
          Third
        </th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>
          a0
        </td>
        <td>
          c0
        </td>
      </tr>
      <tr>
        <td>
          a2
        </td>
        <td>
          c2
        </td>
      </tr>
      <tr>
        <td>
          a1
        </td>
        <td>
          c1
        </td>
      </tr>
    </tbody>
    </table>

This level of control over the way columns are rendered allows for creating
advanced column types.

Formatter Subclasses
====================

The Formatter is useful, but lacks some features you may need.  The
factoring is such that, typically, overriding just a few methods can easily
provide what you need.  The table module provides a few examples of these
subclasses.  While the names are sometimes a bit unwieldy, the functionality is
useful.

AlternatingRowFormatter
-----------------------

The AlternatingRowFormatter is the simplest subclass, offering an
odd-even row formatter that's very easy to use::

    >>> formatter = table.AlternatingRowFormatter(
    ...     context, request, items, ('First', 'Third'), columns=columns)
    >>> print formatter()
    <table>
    <thead>
      <tr>
        <th>
          First
        </th>
        <th>
          Third
        </th>
      </tr>
    </thead>
    <tbody>
      <tr class="odd">
        <td>
          a0
        </td>
        <td>
          c0
        </td>
      </tr>
      <tr class="even">
        <td>
          a2
        </td>
        <td>
          c2
        </td>
      </tr>
      <tr class="odd">
        <td>
          a1
        </td>
        <td>
          c1
        </td>
      </tr>
    </tbody>
    </table>

If you want different classes other than "even" and "odd" then simply
define `row_classes` on your instance: the default is a tuple of "even" and
"odd", but "green" and "red" will work as well:

    >>> formatter.row_classes = ("red", "green")
    >>> print formatter()
    <table>
    <thead>
      <tr>
        <th>
          First
        </th>
        <th>
          Third
        </th>
      </tr>
    </thead>
    <tbody>
      <tr class="green">
        <td>
          a0
        </td>
        <td>
          c0
        </td>
      </tr>
      <tr class="red">
        <td>
          a2
        </td>
        <td>
          c2
        </td>
      </tr>
      <tr class="green">
        <td>
          a1
        </td>
        <td>
          c1
        </td>
      </tr>
    </tbody>
    </table>

Note that this formatter also plays nicely with the other CSS classes defined
by the formatter:

    >>> formatter.cssClasses['tr'] = 'list'
    >>> print formatter()
    <table>
      <thead>
        <tr class="list">
          <th>
            First
          </th>
          <th>
            Third
          </th>
        </tr>
      </thead>
      <tbody>
      <tr class="list green">
        <td>
          a0
        </td>
        <td>
          c0
        </td>
      </tr>
      <tr class="list red">
        <td>
          a2
        </td>
        <td>
          c2
        </td>
      </tr>
      <tr class="list green">
        <td>
          a1
        </td>
        <td>
          c1
        </td>
      </tr>
      </tbody>
    </table>


SortingFormatter
----------------

``SortingFormatter`` supports ``ISortableColumn`` instances by asking them to
sort using the ``ISortableColumn`` interface described above.  Instantiating
one takes a new final optional argument, ``sort_on``, which is a sequence of
tuple pairs of (column name string, reverse sort boolean) in which the first
pair is the primary sort.  Here's an example.  Notice that we are sorting on
the hidden column--this is acceptable, and not even all that unlikely to
encounter.

    >>> formatter = table.SortingFormatter(
    ...     context, request, items, ('First', 'Third'), columns=columns,
    ...     sort_on=(('Second', True),))
    >>> print formatter()
    <table>
    <thead>
      <tr>
        <th>
          First
        </th>
        <th>
          Third
        </th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>
          a2
        </td>
        <td>
          c2
        </td>
      </tr>
      <tr>
        <td>
          a1
        </td>
        <td>
          c1
        </td>
      </tr>
      <tr>
        <td>
          a0
        </td>
        <td>
          c0
        </td>
      </tr>
    </tbody>
    </table>

Sorting can also be done on multiple columns.  This has the effect of
subsorting.  It is up to a column to support the subsorting: it is not a
required behavior.  The default GetterColumns we have been using it support it
at the expense of possibly doing a lot of wasted work; the behavior will come
in handy for some examples, though.

First, we'll add some data items that have the same value in the "First"
column. Then we'll configure the sort to sort with "First" being the primary
key and "Third" being the secondary key (you can provide more than two if you
wish). Note that, unlike some of the values examined up to this point, the
sort columns will only be honored when passed to the class on instanciation.
    >>> big_items = items[:]
    >>> big_items.append(DataItem('a1', 'b1', 'c9'))
    >>> big_items.append(DataItem('a1', 'b1', 'c7'))
    >>> big_items.append(DataItem('a1', 'b1', 'c8'))
    >>> formatter = table.SortingFormatter(
    ...     context, request, big_items, ('First', 'Third'), columns=columns,
    ...     sort_on=(('First', True), ('Third', False)))
    >>> print formatter()
    <table>
    <thead>
      <tr>
        <th>
          First
        </th>
        <th>
          Third
        </th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>
          a2
        </td>
        <td>
          c2
        </td>
      </tr>
      <tr>
        <td>
          a1
        </td>
        <td>
          c1
        </td>
      </tr>
      <tr>
        <td>
          a1
        </td>
        <td>
          c7
        </td>
      </tr>
      <tr>
        <td>
          a1
        </td>
        <td>
          c8
        </td>
      </tr>
      <tr>
        <td>
          a1
        </td>
        <td>
          c9
        </td>
      </tr>
      <tr>
        <td>
          a0
        </td>
        <td>
          c0
        </td>
      </tr>
    </tbody>
    </table>

If the direction of the primary sort is changed, it doesn't effect the sub
sort::

    >>> formatter = table.SortingFormatter(
    ...     context, request, big_items, ('First', 'Third'), columns=columns,
    ...     sort_on=(('First', False), ('Third', False)))
    >>> print formatter()
    <table>
    <thead>
      <tr>
        <th>
          First
        </th>
        <th>
          Third
        </th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>
          a0
        </td>
        <td>
          c0
        </td>
      </tr>
      <tr>
        <td>
          a1
        </td>
        <td>
          c1
        </td>
      </tr>
      <tr>
        <td>
          a1
        </td>
        <td>
          c7
        </td>
      </tr>
      <tr>
        <td>
          a1
        </td>
        <td>
          c8
        </td>
      </tr>
      <tr>
        <td>
          a1
        </td>
        <td>
          c9
        </td>
      </tr>
      <tr>
        <td>
          a2
        </td>
        <td>
          c2
        </td>
      </tr>
    </tbody>
    </table>

When batching sorted tables, the sorting is applied first, then the batching::

    >>> formatter = table.SortingFormatter(
    ...     context, request, items, ('First', 'Third'), columns=columns,
    ...     batch_start=1, sort_on=(('Second', True),))
    >>> print formatter()
    <table>
    <thead>
      <tr>
        <th>
          First
        </th>
        <th>
          Third
        </th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>
          a1
        </td>
        <td>
          c1
        </td>
      </tr>
      <tr>
        <td>
          a0
        </td>
        <td>
          c0
        </td>
      </tr>
    </tbody>
    </table>

StandaloneSortFormatter and FormSortFormatter
---------------------------------------------

The sorting table formatter takes care of the sorting back end, but it's
convenient to encapsulate a bit of the front end logic as well, to provide
columns with clickable headers for sorting and so on without having to write
the code every time you need the behavior.  Two subclasses of
SortingFormatter provide this capability.  The
StandaloneSortFormatter is useful for tables that are not parts of a
form, while the FormSortFormatter is designed to fit within a form.

Both versions look at the request to examine what the user has requested be
sorted, and draw UI on the sortable column headers to enable sorting.  The
standalone version uses javascript to put the information in the url, and
the form version puts the information in a hidden field.

Let's take a look at the output of one of these formatters.  First there will
be no sorting information.

    >>> request = zope.publisher.browser.TestRequest()
    >>> formatter = table.FormSortFormatter(
    ...     context, request, items, ('First', 'Third'), columns=columns)
    >>> print formatter()
    <table>
    <thead>
      <tr>
        <th>
                <span class="zc-table-sortable"
                      onclick="javascript: onSortClickForm(
                            'First', 'sort_on')"
                        onMouseOver="javascript: this.className='sortable zc-table-sortable'"
                        onMouseOut="javascript: this.className='zc-table-sortable'">
                    First</span>...
        </th>
        <th>
                <span class="zc-table-sortable"
                      onclick="javascript: onSortClickForm(
                            'Third', 'sort_on')"
                        onMouseOver="javascript: this.className='sortable zc-table-sortable'"
                        onMouseOut="javascript: this.className='zc-table-sortable'">
                    Third</span>...
        </th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>
          a0
        </td>
        <td>
          c0
        </td>
      </tr>
      <tr>
        <td>
          a2
        </td>
        <td>
          c2
        </td>
      </tr>
      <tr>
        <td>
          a1
        </td>
        <td>
          c1
        </td>
      </tr>
    </tbody>
    </table>
    ...

Setting a prefix also affects the value used to store the sorting information.

    >>> formatter = table.FormSortFormatter(
    ...     context, request, items, ('First', 'Third'),
    ...     prefix='slot.first', columns=columns)
    >>> sort_on_name = table.getSortOnName(formatter.prefix)
    >>> print formatter()
    <table>
    <thead>
      <tr>
        <th>
                <span class="zc-table-sortable"
                      onclick="javascript: onSortClickForm(
                            'First', 'slot.first.sort_on')"
                        onMouseOver="javascript: this.className='sortable zc-table-sortable'"
                        onMouseOut="javascript: this.className='zc-table-sortable'">
                    First</span>...
        </th>
        <th>
                <span class="zc-table-sortable"
                      onclick="javascript: onSortClickForm(
                            'Third', 'slot.first.sort_on')"
                        onMouseOver="javascript: this.className='sortable zc-table-sortable'"
                        onMouseOut="javascript: this.className='zc-table-sortable'">
                    Third</span>...
        </th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>
          a0
        </td>
        <td>
          c0
        </td>
      </tr>
      <tr>
        <td>
          a2
        </td>
        <td>
          c2
        </td>
      </tr>
      <tr>
        <td>
          a1
        </td>
        <td>
          c1
        </td>
      </tr>
    </tbody>
    </table>
    ...

Now we'll add information in the request about the sort, and use a prefix.
The value given in the request indicates that the form should be sorted by
the second column in reverse order.

    >>> request.form[sort_on_name] = ['Second', 'Second']
    >>> formatter = table.FormSortFormatter(
    ...     context, request, items, ('First', 'Third'),
    ...     prefix='slot.first', columns=columns)
    >>> print formatter()
    <table>
    <thead>
      <tr>
        <th>
                <span class="zc-table-sortable"
                      onclick="javascript: onSortClickForm(
                            'First', 'slot.first.sort_on')"
                        onMouseOver="javascript: this.className='sortable zc-table-sortable'"
                        onMouseOut="javascript: this.className='zc-table-sortable'">
                    First</span>...
        </th>
        <th>
                <span class="zc-table-sortable"
                      onclick="javascript: onSortClickForm(
                            'Third', 'slot.first.sort_on')"
                        onMouseOver="javascript: this.className='sortable zc-table-sortable'"
                        onMouseOut="javascript: this.className='zc-table-sortable'">
                    Third</span>...
        </th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>
          a2
        </td>
        <td>
          c2
        </td>
      </tr>
      <tr>
        <td>
          a1
        </td>
        <td>
          c1
        </td>
      </tr>
      <tr>
        <td>
          a0
        </td>
        <td>
          c0
        </td>
      </tr>
    </tbody>
    </table>
    ...

Note that sort_on value explicitly passed to a FormSortFormatter is only an
initial value: if the request contains sort information, then the sort_on
value is ignored.  This is correct behavior because the initial sort_on value
is recorded in the form, and does not need to be repeated.

For instance, if we re-use the big_items collection from above and pass a
sort_on but modify the request to effectively get a sort_on of
(('First', True), ('Third', False)), then the code will look something like
this--notice that we draw arrows indicating the direction of the primary
search.

    >>> request = zope.publisher.browser.TestRequest()
    >>> request.form[sort_on_name] = ['Third', 'First', 'First'] # LIFO
    >>> formatter = table.FormSortFormatter(
    ...     context, request, big_items, ('First', 'Third'), columns=columns,
    ...     prefix='slot.first', sort_on=(('Second', False), ('Third', True)))
    >>> interfaces.IColumnSortedItems.providedBy(formatter.items)
    True
    >>> zope.interface.verify.verifyObject(interfaces.IColumnSortedItems,
    ...                                    formatter.items)
    True
    >>> formatter.items.sort_on
    [['First', True], ['Third', False]]
    >>> print formatter()
    <table>
    <thead>
      <tr>
        <th>
                <span class="zc-table-sortable"
                      onclick="javascript: onSortClickForm(
                            'First', 'slot.first.sort_on')"
                        onMouseOver="javascript: this.className='sortable zc-table-sortable'"
                        onMouseOut="javascript: this.className='zc-table-sortable'">
                    First</span>...
                    <img src="/@@/zc.table/sort_arrows_up.gif".../>
        </th>
        <th>
                <span class="zc-table-sortable"
                      onclick="javascript: onSortClickForm(
                            'Third', 'slot.first.sort_on')"
                        onMouseOver="javascript: this.className='sortable zc-table-sortable'"
                        onMouseOut="javascript: this.className='zc-table-sortable'">
                    Third</span>...
        </th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>
          a2
        </td>
        <td>
          c2
        </td>
      </tr>
      <tr>
        <td>
          a1
        </td>
        <td>
          c1
        </td>
      </tr>
      <tr>
        <td>
          a1
        </td>
        <td>
          c7
        </td>
      </tr>
      <tr>
        <td>
          a1
        </td>
        <td>
          c8
        </td>
      </tr>
      <tr>
        <td>
          a1
        </td>
        <td>
          c9
        </td>
      </tr>
      <tr>
        <td>
          a0
        </td>
        <td>
          c0
        </td>
      </tr>
    </tbody>
    </table>
    ...

The standalone non-form version uses almost all the same code but doesn't
draw the hidden field and calls a different JavaScript function (which puts the
sorting information in the query string rather than in a form field).  Here's a
quick copy of the example above, modified to use the standalone version.
Because of the way the query string is used, more than two instances of a
column name may appear in the form field, so this is emulated in the example.

Because the standalone version doesn't have a form to record the initial
sort_on values, they are honored even if sort_on values exist in the request.
This is in direct contrast to the form-based formatter discussed immediately
above.

    >>> request = zope.publisher.browser.TestRequest()
    >>> request.form[sort_on_name] = [
    ...     'Third', 'First', 'Second', 'Third', 'Second', 'Third', 'First']
    ... # == First True, Third False, Second True
    >>> formatter = table.StandaloneSortFormatter(
    ...     context, request, big_items, ('First', 'Third'), columns=columns,
    ...     prefix='slot.first', sort_on=(('Second', False), ('Third', True)))
    >>> formatter.items.sort_on
    [['First', True], ['Third', False], ['Second', False]]
    >>> print formatter()
    <table>
    <thead>
      <tr>
        <th>
                <span class="zc-table-sortable"
                      onclick="javascript: onSortClickStandalone(
                            'First', 'slot.first.sort_on')"
                        onMouseOver="javascript: this.className='sortable zc-table-sortable'"
                        onMouseOut="javascript: this.className='zc-table-sortable'">
                    First</span> <img src="/@@/zc.table/sort_arrows_up.gif".../>
        </th>
        <th>
                <span class="zc-table-sortable"
                      onclick="javascript: onSortClickStandalone(
                            'Third', 'slot.first.sort_on')"
                        onMouseOver="javascript: this.className='sortable zc-table-sortable'"
                        onMouseOut="javascript: this.className='zc-table-sortable'">
                    Third</span>...
        </th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>
          a2
        </td>
        <td>
          c2
        </td>
      </tr>
      <tr>
        <td>
          a1
        </td>
        <td>
          c1
        </td>
      </tr>
      <tr>
        <td>
          a1
        </td>
        <td>
          c7
        </td>
      </tr>
      <tr>
        <td>
          a1
        </td>
        <td>
          c8
        </td>
      </tr>
      <tr>
        <td>
          a1
        </td>
        <td>
          c9
        </td>
      </tr>
      <tr>
        <td>
          a0
        </td>
        <td>
          c0
        </td>
      </tr>
    </tbody>
    </table>

The sorting code is to be able to accept iterators as items, and only iterate
through them as much as necessary to accomplish the tasks.  This needs to
support multiple simultaneous iterations.  Another goal is to use the slice
syntax to let sort implementations be guided as to where precise sorting is
needed, in case n-best or other approaches can be used.

There is some trickiness about this in the implementation, and this part of
the document tries to explore some of the edge cases that have proved
problematic in the field.

In particular, we should examine using an iterator in sorted and unsorted
configurations within a sorting table formatter, with batching.

Unsorted:

    >>> formatter = table.SortingFormatter(
    ...     context, request, iter(items), ('First', 'Third'),
    ...     columns=columns, batch_size=2)
    >>> formatter.items[0] is not None # artifically provoke error :-(
    True
    >>> print formatter()
    <table>
    <thead>
      <tr>
        <th>
          First
        </th>
        <th>
          Third
        </th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>
          a0
        </td>
        <td>
          c0
        </td>
      </tr>
      <tr>
        <td>
          a2
        </td>
        <td>
          c2
        </td>
      </tr>
    </tbody>
    </table>

Sorted:

    >>> formatter = table.SortingFormatter(
    ...     context, request, iter(items), ('First', 'Third'),
    ...     columns=columns, sort_on=(('Second', True),), batch_size=2)
    >>> formatter.items[0] is not None # artifically provoke error :-(
    True
    >>> print formatter()
    <table>
    <thead>
      <tr>
        <th>
          First
        </th>
        <th>
          Third
        </th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>
          a2
        </td>
        <td>
          c2
        </td>
      </tr>
      <tr>
        <td>
          a1
        </td>
        <td>
          c1
        </td>
      </tr>
    </tbody>
    </table>
