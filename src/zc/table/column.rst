Useful column types
===================

We provide a number of pre-defined column types to use in table
definitions.

Field Edit Columns
------------------

Field edit columns provide support for tables of input widgets.
To define a field edit column, you need to provide:

  - title, the label to be displayed

  - a prefix, which is used to distinguish a columns inputs
    from those of other columns

  - a field that describes the type of data in the column

  - an id getter

  - an optional data getter, and

  - an optional data setter

The id getter has to compute a string that uniquely identified an
item.

Let's look at a simple example.  We have a collection of contacts,
with names and email addresses:

    >>> import re
    >>> from zope import schema, interface
    >>> class IContact(interface.Interface):
    ...     name = schema.TextLine()
    ...     email = schema.TextLine(
    ...             constraint=re.compile(r'\w+@\w+([.]\w+)+$').match)

    >>> @interface.implementer(IContact)
    ... class Contact:
    ...     def __init__(self, id, name, email):
    ...         self.id = id
    ...         self.name = name
    ...         self.email = email

    >>> contacts = (
    ...     Contact('1', 'Bob Smith', 'bob@zope.com'),
    ...     Contact('2', 'Sally Baker', 'sally@zope.com'),
    ...     Contact('3', 'Jethro Tul', 'jethro@zope.com'),
    ...     Contact('4', 'Joe Walsh', 'joe@zope.com'),
    ...     )

We'll define columns that allow us to display and edit name and
email addresses.

    >>> from zc.table import column
    >>> columns = (
    ...     column.FieldEditColumn(
    ...         "Name", "test", IContact["name"],
    ...         lambda contact: contact.id,
    ...         ),
    ...     column.FieldEditColumn(
    ...         "Email address", "test", IContact["email"],
    ...         lambda contact: contact.id,
    ...         ),
    ...     )

Now, with this, we can create a table with input widgets.  The columns don't
need a context other than the items themselves, so we ignore that part of the
table formatter instantiation:

    >>> from zc import table
    >>> import zope.publisher.browser
    >>> request = zope.publisher.browser.TestRequest()
    >>> context = None
    >>> formatter = table.Formatter(
    ...     context, request, contacts, columns=columns)
    >>> print(formatter())
    <table>
    <thead>
      <tr>
        <th>
          Name
        </th>
        <th>
          Email address
        </th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>
          <input class="textType" id="test.MQ==.name" name="test.MQ==.name"
                 size="20" type="text" value="Bob Smith"  />
        </td>
        <td>
          <input class="textType" id="test.MQ==.email" name="test.MQ==.email"
                 size="20" type="text" value="bob@zope.com"  />
        </td>
      </tr>
      <tr>
        <td>
          <input class="textType" id="test.Mg==.name" name="test.Mg==.name"
                 size="20" type="text" value="Sally Baker"  />
        </td>
        <td>
          <input class="textType" id="test.Mg==.email" name="test.Mg==.email"
                 size="20" type="text" value="sally@zope.com"  />
        </td>
      </tr>
      <tr>
        <td>
          <input class="textType" id="test.Mw==.name" name="test.Mw==.name"
                 size="20" type="text" value="Jethro Tul"  />
        </td>
        <td>
          <input class="textType" id="test.Mw==.email" name="test.Mw==.email"
                 size="20" type="text" value="jethro@zope.com"  />
        </td>
      </tr>
      <tr>
        <td>
          <input class="textType" id="test.NA==.name" name="test.NA==.name"
                 size="20" type="text" value="Joe Walsh"  />
        </td>
        <td>
          <input class="textType" id="test.NA==.email" name="test.NA==.email"
                 size="20" type="text" value="joe@zope.com"  />
        </td>
      </tr>
    </tbody>
    </table>

Note that the input names include base64 encodings of the item ids.

If the request has input for a value, then this will override item data:

    >>> request.form["test.NA==.email"] = 'walsh@zope.com'
    >>> print(formatter())
    <table>
    <thead>
      <tr>
        <th>
          Name
        </th>
        <th>
          Email address
        </th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>
          <input class="textType" id="test.MQ==.name" name="test.MQ==.name"
                 size="20" type="text" value="Bob Smith"  />
        </td>
        <td>
          <input class="textType" id="test.MQ==.email" name="test.MQ==.email"
                 size="20" type="text" value="bob@zope.com"  />
        </td>
      </tr>
      <tr>
        <td>
          <input class="textType" id="test.Mg==.name" name="test.Mg==.name"
                 size="20" type="text" value="Sally Baker"  />
        </td>
        <td>
          <input class="textType" id="test.Mg==.email" name="test.Mg==.email"
                 size="20" type="text" value="sally@zope.com"  />
        </td>
      </tr>
      <tr>
        <td>
          <input class="textType" id="test.Mw==.name" name="test.Mw==.name"
                 size="20" type="text" value="Jethro Tul"  />
        </td>
        <td>
          <input class="textType" id="test.Mw==.email" name="test.Mw==.email"
                 size="20" type="text" value="jethro@zope.com"  />
        </td>
      </tr>
      <tr>
        <td>
          <input class="textType" id="test.NA==.name" name="test.NA==.name"
                 size="20" type="text" value="Joe Walsh"  />
        </td>
        <td>
          <input class="textType" id="test.NA==.email" name="test.NA==.email"
                 size="20" type="text" value="walsh@zope.com"  />
        </td>
      </tr>
    </tbody>
    </table>

and the contact data is unchanged:

    >>> contacts[3].email
    'joe@zope.com'

Field edit columns provide methods for getting and validating input
data, and fpr updating the undelying data:

    >>> data = columns[1].input(contacts, request)
    >>> data
    {'NA==': 'walsh@zope.com'}

The data returned is a mapping from item id to input value.  Items
that don't have input are ignored.  The data can be used with the
update function to update the underlying data:

    >>> columns[1].update(contacts, data)
    True

    >>> contacts[3].email
    'walsh@zope.com'

Note that the update function returns a boolean value indicating
whether any changes were made:

    >>> columns[1].update(contacts, data)
    False

The input function also validates input.  If there are any errors, a
WidgetsError will be raised:

    >>> request.form["test.NA==.email"] = 'walsh'
    >>> data = columns[1].input(contacts, request)
    Traceback (most recent call last):
    ...
    zope.formlib.interfaces.WidgetsError: WidgetInputError:
        ('email', '', ConstraintNotSatisfied('walsh', 'email'))


Custom getters and setters
--------------------------

Normally, the given fields getter and setter is used, however, custom
getters and setters can be provided.  Let's look at an example of
a bit table:

    >>> data = [0, 0], [1, 1], [2, 2], [3, 3]

    >>> def setbit(data, bit, value):
    ...     value = bool(value) << bit
    ...     mask = 1 << bit
    ...     data[1] = ((data[1] | mask) ^ mask) | value
    >>> columns = (
    ...     column.FieldEditColumn(
    ...         "Bit 0", "test", schema.Bool(__name__='0'),
    ...         lambda data: str(data[0]),
    ...         getter = lambda data: 1&(data[1]),
    ...         setter = lambda data, v: setbit(data, 0, v),
    ...         ),
    ...     column.FieldEditColumn(
    ...         "Bit 1", "test", schema.Bool(__name__='1'),
    ...         lambda data: str(data[0]),
    ...         getter = lambda data: 2&(data[1]),
    ...         setter = lambda data, v: setbit(data, 1, v),
    ...         ),
    ...     )

    >>> context = None # not needed
    >>> request = zope.publisher.browser.TestRequest()
    >>> formatter = table.Formatter(
    ...     context, request, data, columns=columns)
    >>> print(formatter())
    <table>
    <thead>
      <tr>
        <th>
          Bit 0
        </th>
        <th>
          Bit 1
        </th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>
          <input class="hiddenType" id="test.MA==.0.used"
                 name="test.MA==.0.used" type="hidden" value="" />
          <input class="checkboxType" id="test.MA==.0"
                 name="test.MA==.0" type="checkbox" value="on"  />
        </td>
        <td>
          <input class="hiddenType" id="test.MA==.1.used"
                 name="test.MA==.1.used" type="hidden" value="" />
          <input class="checkboxType" id="test.MA==.1"
                 name="test.MA==.1" type="checkbox" value="on"  />
        </td>
      </tr>
      <tr>
        <td>
          <input class="hiddenType" id="test.MQ==.0.used"
                 name="test.MQ==.0.used" type="hidden" value="" />
          <input class="checkboxType" checked="checked" id="test.MQ==.0"
                 name="test.MQ==.0" type="checkbox" value="on"  />
        </td>
        <td>
          <input class="hiddenType" id="test.MQ==.1.used"
                 name="test.MQ==.1.used" type="hidden" value="" />
          <input class="checkboxType" id="test.MQ==.1"
                 name="test.MQ==.1" type="checkbox" value="on"  />
        </td>
      </tr>
      <tr>
        <td>
          <input class="hiddenType" id="test.Mg==.0.used"
                 name="test.Mg==.0.used" type="hidden" value="" />
          <input class="checkboxType" id="test.Mg==.0"
                 name="test.Mg==.0" type="checkbox" value="on"  />
        </td>
        <td>
          <input class="hiddenType" id="test.Mg==.1.used"
                 name="test.Mg==.1.used" type="hidden" value="" />
          <input class="checkboxType" checked="checked" id="test.Mg==.1"
                 name="test.Mg==.1" type="checkbox" value="on"  />
        </td>
      </tr>
      <tr>
        <td>
          <input class="hiddenType" id="test.Mw==.0.used"
                 name="test.Mw==.0.used" type="hidden" value="" />
          <input class="checkboxType" checked="checked" id="test.Mw==.0"
                 name="test.Mw==.0" type="checkbox" value="on"  />
        </td>
        <td>
          <input class="hiddenType" id="test.Mw==.1.used"
                 name="test.Mw==.1.used" type="hidden" value="" />
          <input class="checkboxType" checked="checked" id="test.Mw==.1"
                 name="test.Mw==.1" type="checkbox" value="on"  />
        </td>
      </tr>
    </tbody>
    </table>

    >>> request.form["test.Mw==.1.used"] = ""
    >>> request.form["test.MA==.1.used"] = ""
    >>> request.form["test.MA==.1"] = "on"

    >>> input = columns[1].input(data, request)
    >>> from pprint import pprint
    >>> pprint(input)
    {'MA==': True,
     'Mw==': False}

    >>> columns[1].update(data, input)
    True

    >>> data
    ([0, 2], [1, 1], [2, 2], [3, 1])

Column names
============

When defining columns, you can supply separate names and titles. You
would do this, for example, to use a blank title:

    >>> columns = (
    ...     column.FieldEditColumn(
    ...         "", "test", schema.Bool(__name__='0'),
    ...         lambda data: str(data[0]),
    ...         getter = lambda data: 1&(data[1]),
    ...         setter = lambda data, v: setbit(data, 0, v),
    ...         name = "0",
    ...         ),
    ...     column.FieldEditColumn(
    ...         "", "test", schema.Bool(__name__='1'),
    ...         lambda data: str(data[0]),
    ...         getter = lambda data: 2&(data[1]),
    ...         setter = lambda data, v: setbit(data, 1, v),
    ...         name = "1",
    ...         ),
    ...     )

    >>> formatter = table.Formatter(
    ...     context, request, data[0:1], columns=columns)
    >>> print(formatter())
    <table>
    <thead>
      <tr>
        <th>
    <BLANKLINE>
        </th>
        <th>
    <BLANKLINE>
        </th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>
          <input class="hiddenType" id="test.MA==.0.used"
                 name="test.MA==.0.used" type="hidden" value="" />
          <input class="checkboxType" id="test.MA==.0"
                 name="test.MA==.0" type="checkbox" value="on"  />
        </td>
        <td>
          <input class="hiddenType" id="test.MA==.1.used"
                 name="test.MA==.1.used" type="hidden" value="" />
          <input class="checkboxType" checked="checked" id="test.MA==.1"
                 name="test.MA==.1" type="checkbox" value="on"  />
        </td>
      </tr>
    </tbody>
    </table>

<>& encoding bug
================

There was a bug in column.py, it did not encode the characters <>& to
&lt; &gt; &amp;

    >>> bugcontacts = (
    ...     Contact('1', 'Bob <Smith>', 'bob@zope.com'),
    ...     Contact('2', 'Sally & Baker', 'sally@zope.com'),
    ...     )

We'll define columns that displays name and email addresses.

    >>> from zc.table import column
    >>> bugcolumns = (
    ...     column.GetterColumn(
    ...         title="Name", name="name",
    ...         getter=lambda contact, formatter: contact.name,
    ...         ),
    ...     column.GetterColumn(
    ...         title="E-mail", name="email",
    ...         getter=lambda contact, formatter: contact.email,
    ...         ),
    ...     )

    >>> request = zope.publisher.browser.TestRequest()
    >>> context = None
    >>> formatter = table.Formatter(
    ...     context, request, bugcontacts, columns=bugcolumns)
    >>> print(formatter())
    <table>
      <thead>
        <tr>
          <th>
            Name
          </th>
          <th>
            E-mail
          </th>
        </tr>
      </thead>
      <tbody>
      <tr>
        <td>
          Bob &#60;Smith&#62;
        </td>
        <td>
          bob@zope.com
        </td>
      </tr>
      <tr>
        <td>
          Sally &#38; Baker
        </td>
        <td>
          sally@zope.com
        </td>
      </tr>
      </tbody>
    </table>

    >>> from zc.table import column
    >>> bug2columns = (
    ...     column.FieldEditColumn(
    ...         "Name", "test", IContact["name"],
    ...         lambda contact: contact.id,
    ...         ),
    ...     column.FieldEditColumn(
    ...         "Email address", "test", IContact["email"],
    ...         lambda contact: contact.id,
    ...         ),
    ...     )

    >>> formatter = table.Formatter(
    ...     context, request, bugcontacts, columns=bug2columns)
    >>> print(formatter())
    <BLANKLINE>
    <table>
      <thead>
        <tr>
          <th>
            Name
          </th>
          <th>
            Email address
          </th>
        </tr>
      </thead>
      <tbody>
      <tr>
        <td>
          <input class="textType" id="test.MQ==.name" name="test.MQ==.name"
                 size="20" type="text" value="Bob &lt;Smith&gt;"  />
        </td>
        <td>
          <input class="textType" id="test.MQ==.email" name="test.MQ==.email"
                 size="20" type="text" value="bob@zope.com"  />
        </td>
      </tr>
      <tr>
        <td>
          <input class="textType" id="test.Mg==.name" name="test.Mg==.name"
                 size="20" type="text" value="Sally &amp; Baker"  />
        </td>
        <td>
          <input class="textType" id="test.Mg==.email" name="test.Mg==.email"
                 size="20" type="text" value="sally@zope.com"  />
        </td>
      </tr>
      </tbody>
    </table>
    <BLANKLINE>
