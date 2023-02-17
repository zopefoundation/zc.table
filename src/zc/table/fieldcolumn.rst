FieldColumn
===========

The FieldColumn is intended to be a replacement for the FieldEditColumn.  It
has the following goals.

- Support the standard column pattern of instantiating a single module global
  column set, and using formatters to store and access information about a
  single given rendering.  The formatter has annotations, prefix, context, and
  request, all of which are desired or even essential for various derived
  columns.  Generally, the formatter has state that the columns need.

- Support display widgets, in addition to input widgets.

- Support formlib form fields, to support custom widgets and other formlib
  field features.

It also has an important design difference.  Rather than relying on functions
passed at initialization for column customization, the field column returns to
a standard subclass design.  The column expects that any of the following
methods may be overridden:

- getId(item, formatter): given an item whose value is to be displayed in the
  column, return a form-friendly string identifier, unique to the item.  We
  define 'form-friendly' as containing characters that are alphanumeric or a
  space, a plus, a slash, or an equals sign (that is, the standard characters
  used in MIME-based base64, excluding new lines).

- get(item, formatter): return the current value for the item.

- set(item, value, formatter): set the given value for the item.

- getFieldContext(item, formatter): return a context to which a field should
  be bound, or None.

- renderCell(item, formatter): the standard rendering of a cell

- renderHeader(formatter): the standard rendering of a column header.

Without subclassing, the column uses field.get and field.set to get and set
values, returns None for bound context, and just renders the field's widget for
the cell, and the title for the header.  Let's look at the default behavior.
We'll use a modified version of the examples given for the FieldEditColumn in
column.txt.

To create a FieldColumn, you must minimally provide a schema field or form
field.  If title is not provided, it is the field's title, or empty if the
field has no title.  A explicit title of an empty string is acceptable and will
be honored.  If name is not provided, it is the field's __name__.

Let's look at a simple example.  We have a collection of contacts,
with names and email addresses:

    >>> import re
    >>> from zope import schema, interface
    >>> class IContact(interface.Interface):
    ...     name = schema.TextLine(title='Name')
    ...     email = schema.TextLine(
    ...             title='Email Address',
    ...             constraint=re.compile(r'\w+@\w+([.]\w+)+$').match)
    ...     salutation = schema.Choice(
    ...             title='Salutation',
    ...             values = ['Mr','Ms'],
    ...             )

    >>> @interface.implementer(IContact)
    ... class Contact:
    ...     def __init__(self, id, name, email, salutation):
    ...         self.id = id
    ...         self.name = name
    ...         self.email = email
    ...         self.salutation = salutation

    >>> contacts = (
    ...     Contact('1', 'Bob Smith', 'bob@zope.com', 'Mr'),
    ...     Contact('2', 'Sally Baker', 'sally@zope.com', 'Ms'),
    ...     Contact('3', 'Jethro Tul', 'jethro@zope.com', 'Mr'),
    ...     Contact('4', 'Joe Walsh', 'joe@zope.com', 'Mr'),
    ...     )

We'll define columns that allow us to display and edit name and
email addresses.

    >>> from zc.table import fieldcolumn
    >>> class ContactColumn(fieldcolumn.FieldColumn):
    ...     def getId(self, item, formatter):
    ...         return fieldcolumn.toSafe(item.id)
    ...
    >>> class BindingContactColumn(ContactColumn):
    ...     def getFieldContext(self, item, formatter):
    ...         return item
    ...
    >>> columns = (ContactColumn(IContact["name"]),
    ...            ContactColumn(IContact["email"]),
    ...            BindingContactColumn(IContact["salutation"])
    ...            )

Now, with this, we can create a table with input widgets.  The columns don't
need a context other than the items themselves, so we ignore that part of the
table formatter instantiation:

    >>> from zc import table
    >>> import zope.publisher.browser
    >>> request = zope.publisher.browser.TestRequest()
    >>> context = None
    >>> formatter = table.Formatter(
    ...     context, request, contacts, columns=columns, prefix='test')
    >>> print(formatter())
    <table>
    <thead>
      <tr>
        <th>
          Name
        </th>
        <th>
          Email Address
        </th>
        <th>
          Salutation
        </th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>
          <input class="textType" id="test.1.name" name="test.1.name"
                 size="20" type="text" value="Bob Smith"  />
        </td>
        <td>
          <input class="textType" id="test.1.email" name="test.1.email"
                 size="20" type="text" value="bob@zope.com"  />
        </td>
        <td>
          <div>
            <div class="value">
              <select id="test.1.salutation" name="test.1.salutation"
                      size="1" >
                <option selected="selected" value="Mr">Mr</option>
                <option value="Ms">Ms</option>
              </select>
            </div>
            <input name="test.1.salutation-empty-marker" type="hidden"
                   value="1" />
          </div>
        </td>
      </tr>
      <tr>
        <td>
          <input class="textType" id="test.2.name" name="test.2.name"
                 size="20" type="text" value="Sally Baker"  />
        </td>
        <td>
          <input class="textType" id="test.2.email" name="test.2.email"
                 size="20" type="text" value="sally@zope.com"  />
        </td>
        <td>
          <div>
            <div class="value">
              <select id="test.2.salutation" name="test.2.salutation"
                      size="1" >
                <option value="Mr">Mr</option>
                <option selected="selected" value="Ms">Ms</option>
              </select>
            </div>
            <input name="test.2.salutation-empty-marker" type="hidden"
                   value="1" />
          </div>
        </td>
      </tr>
      <tr>
        <td>
          <input class="textType" id="test.3.name" name="test.3.name"
                 size="20" type="text" value="Jethro Tul"  />
        </td>
        <td>
          <input class="textType" id="test.3.email" name="test.3.email"
                 size="20" type="text" value="jethro@zope.com"  />
        </td>
        <td>
          <div>
            <div class="value">
              <select id="test.3.salutation" name="test.3.salutation"
                      size="1" >
                <option selected="selected" value="Mr">Mr</option>
                <option value="Ms">Ms</option>
              </select>
            </div>
            <input name="test.3.salutation-empty-marker" type="hidden"
                   value="1" />
          </div>
        </td>
      </tr>
      <tr>
        <td>
          <input class="textType" id="test.4.name" name="test.4.name"
                 size="20" type="text" value="Joe Walsh"  />
        </td>
        <td>
          <input class="textType" id="test.4.email" name="test.4.email"
                 size="20" type="text" value="joe@zope.com"  />
        </td>
        <td>
          <div>
            <div class="value">
              <select id="test.4.salutation" name="test.4.salutation"
                      size="1" >
                <option selected="selected" value="Mr">Mr</option>
                <option value="Ms">Ms</option>
              </select>
            </div>
            <input name="test.4.salutation-empty-marker" type="hidden"
                   value="1" />
          </div>
        </td>
      </tr>
    </tbody>
    </table>

Note that the input names do not include base64 encodings of the item ids
because they already match the necessary constraints.

If the request has input for a value, then this will override item data:

    >>> request.form["test.4.email"] = 'walsh@zope.com'
    >>> print(formatter())
    <table>
    <thead>
      <tr>
        <th>
          Name
        </th>
        <th>
          Email Address
        </th>
        <th>
          Salutation
        </th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>
          <input class="textType" id="test.1.name" name="test.1.name"
                 size="20" type="text" value="Bob Smith"  />
        </td>
        <td>
          <input class="textType" id="test.1.email" name="test.1.email"
                 size="20" type="text" value="bob@zope.com"  />
        </td>
        <td>
          <div>
            <div class="value">
              <select id="test.1.salutation" name="test.1.salutation"
                      size="1" >
                <option selected="selected" value="Mr">Mr</option>
                <option value="Ms">Ms</option>
              </select>
            </div>
            <input name="test.1.salutation-empty-marker" type="hidden"
                   value="1" />
          </div>
        </td>
      </tr>
      <tr>
        <td>
          <input class="textType" id="test.2.name" name="test.2.name"
                 size="20" type="text" value="Sally Baker"  />
        </td>
        <td>
          <input class="textType" id="test.2.email" name="test.2.email"
                 size="20" type="text" value="sally@zope.com"  />
        </td>
        <td>
          <div>
            <div class="value">
              <select id="test.2.salutation" name="test.2.salutation"
                      size="1" >
                <option value="Mr">Mr</option>
                <option selected="selected" value="Ms">Ms</option>
              </select>
            </div>
            <input name="test.2.salutation-empty-marker" type="hidden"
                   value="1" />
          </div>
        </td>
      </tr>
      <tr>
        <td>
          <input class="textType" id="test.3.name" name="test.3.name"
                 size="20" type="text" value="Jethro Tul"  />
        </td>
        <td>
          <input class="textType" id="test.3.email" name="test.3.email"
                 size="20" type="text" value="jethro@zope.com"  />
        </td>
        <td>
          <div>
            <div class="value">
              <select id="test.3.salutation" name="test.3.salutation"
                      size="1" >
                <option selected="selected" value="Mr">Mr</option>
                <option value="Ms">Ms</option>
              </select>
            </div>
            <input name="test.3.salutation-empty-marker" type="hidden"
                   value="1" />
          </div>
        </td>
      </tr>
      <tr>
        <td>
          <input class="textType" id="test.4.name" name="test.4.name"
                 size="20" type="text" value="Joe Walsh"  />
        </td>
        <td>
          <input class="textType" id="test.4.email" name="test.4.email"
                 size="20" type="text" value="walsh@zope.com"  />
        </td>
        <td>
          <div>
            <div class="value">
              <select id="test.4.salutation" name="test.4.salutation"
                      size="1" >
                <option selected="selected" value="Mr">Mr</option>
                <option value="Ms">Ms</option>
              </select>
            </div>
            <input name="test.4.salutation-empty-marker" type="hidden"
                   value="1" />
          </div>
        </td>
      </tr>
    </tbody>
    </table>

and the contact data is unchanged:

    >>> contacts[3].email
    'joe@zope.com'

Field edit columns provide methods for getting and validating input
data, and for updating the undelying data:

    >>> data = columns[1].input(contacts, formatter)
    >>> data
    {'4': 'walsh@zope.com'}

The data returned is a mapping from item id to input value.  Items
that don't have input are ignored.  The data can be used with the
update function to update the underlying data:

    >>> columns[1].update(contacts, data, formatter)
    True

    >>> contacts[3].email
    'walsh@zope.com'

Note that the update function returns a boolean value indicating
whether any changes were made:

    >>> columns[1].update(contacts, data, formatter)
    False

The input function also validates input.  If there are any errors, a
WidgetsError will be raised:

    >>> request.form["test.4.email"] = 'walsh'
    >>> try:
    ...     data = columns[1].input(contacts, formatter)
    ... except zope.formlib.interfaces.WidgetsError as e:
    ...     e
    WidgetInputError: ('email', 'Email Address', ConstraintNotSatisfied('walsh', 'email'))

Custom getters and setters
--------------------------

Normally, the given fields getter and setter is used, however, custom
getters and setters can be provided.  Let's look at an example of
a bit table:

    >>> data = [0, 0], [1, 1], [2, 2], [3, 3]

    >>> class BitColumn(fieldcolumn.FieldColumn):
    ...     def __init__(self, field, bit, title=None, name=''):
    ...         super(BitColumn, self).__init__(field, title, name)
    ...         self.bit = bit
    ...     def getId(self, item, formatter):
    ...         return str(item[0])
    ...     def get(self, item, formatter):
    ...         return (1 << self.bit)&(item[1])
    ...     def set(self, item, value, formatter):
    ...         value = bool(value) << self.bit
    ...         mask = 1 << self.bit
    ...         item[1] = ((item[1] | mask) ^ mask) | value

    >>> columns = (
    ...     BitColumn(schema.Bool(__name__='0', title='Bit 0'), 0),
    ...     BitColumn(schema.Bool(__name__='1', title='Bit 1'), 1))

    >>> context = None # not needed
    >>> request = zope.publisher.browser.TestRequest()
    >>> formatter = table.Formatter(
    ...     context, request, data, columns=columns, prefix='test')
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
          <input class="hiddenType" id="test.0.0.used"
                 name="test.0.0.used" type="hidden" value="" />
          <input class="checkboxType" id="test.0.0"
                 name="test.0.0" type="checkbox" value="on"  />
        </td>
        <td>
          <input class="hiddenType" id="test.0.1.used"
                 name="test.0.1.used" type="hidden" value="" />
          <input class="checkboxType" id="test.0.1"
                 name="test.0.1" type="checkbox" value="on"  />
        </td>
      </tr>
      <tr>
        <td>
          <input class="hiddenType" id="test.1.0.used"
                 name="test.1.0.used" type="hidden" value="" />
          <input class="checkboxType" checked="checked" id="test.1.0"
                 name="test.1.0" type="checkbox" value="on"  />
        </td>
        <td>
          <input class="hiddenType" id="test.1.1.used"
                 name="test.1.1.used" type="hidden" value="" />
          <input class="checkboxType" id="test.1.1"
                 name="test.1.1" type="checkbox" value="on"  />
        </td>
      </tr>
      <tr>
        <td>
          <input class="hiddenType" id="test.2.0.used"
                 name="test.2.0.used" type="hidden" value="" />
          <input class="checkboxType" id="test.2.0"
                 name="test.2.0" type="checkbox" value="on"  />
        </td>
        <td>
          <input class="hiddenType" id="test.2.1.used"
                 name="test.2.1.used" type="hidden" value="" />
          <input class="checkboxType" checked="checked" id="test.2.1"
                 name="test.2.1" type="checkbox" value="on"  />
        </td>
      </tr>
      <tr>
        <td>
          <input class="hiddenType" id="test.3.0.used"
                 name="test.3.0.used" type="hidden" value="" />
          <input class="checkboxType" checked="checked" id="test.3.0"
                 name="test.3.0" type="checkbox" value="on"  />
        </td>
        <td>
          <input class="hiddenType" id="test.3.1.used"
                 name="test.3.1.used" type="hidden" value="" />
          <input class="checkboxType" checked="checked" id="test.3.1"
                 name="test.3.1" type="checkbox" value="on"  />
        </td>
      </tr>
    </tbody>
    </table>

    >>> request.form["test.3.1.used"] = ""
    >>> request.form["test.0.1.used"] = ""
    >>> request.form["test.0.1"] = "on"

    >>> input = columns[1].input(data, formatter)
    >>> from pprint import pprint
    >>> pprint(input)
    {'0': True,
     '3': False}

    >>> columns[1].update(data, input, formatter)
    True

    >>> data
    ([0, 2], [1, 1], [2, 2], [3, 1])
