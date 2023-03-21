# Internal Form Structure
To ease [database structure](Database-Structure) updates, a form definition language was created to serialize the various data entry points to prevent each client to be updated each time a new field is added (or changed) on the OpenTera platform.

By querying the [form API](API), a client can request a form structure definition for a specific data type. Furthermore, when that form definition contains lists, that [API](API) can also be used to filter only relevant data for the current context.

Forms are serialized using JSON-formatted strings. Implementation on the OpenTera server can be found in the [`TeraForm`](https://github.com/introlab/opentera/blob/main/teraserver/python/opentera/forms/TeraForm.py), and the implementation for each data type can be found in the [`forms`](https://github.com/introlab/opentera/tree/main/teraserver/python/opentera/forms) folder.

## Forms hierarchy
Forms follow the following hierarchy:
```
{
  'objecttype': <name of [database object type](Database-Structure)>,
  'sections': [  # List of the various sections in the form
                 {
                   ...
                   'items': [  # List of the various fields composing the form
                              {
                                ...
                              }
                            ]
                 }
              ]
}
```

Basically, a form can have multiple sections each of them having multiple items (fields). It is up to the client implementation to properly display those sections and items.

## Form sections
A form section is a logical way to organize items. In most forms, there will only be one section, but it is possible to define as many sections as required. **At least one form section is required for any form**.

The form section section(!) has the following fields:
* `id`, the section internal id. Could be anything, only to help with display purpose client-side
* `label`, the section label that needs to be displayed on the form. [Translated](Translations) on the server when queried.
* `_order`, the order into which to display that particular section. Lower numbers are displayed first.
* `items`, a list of the various items part of that section (see below).

## Form items
An item represents a field. This is the most complicated element of a form, as conditions, default values and various flags can be added to an item.

The items each have the following describing fields:
* `id`, the id of that item. If directly linked to a [database object](Database-Structure), this is the name of the field in the database.
* `label`, the item label that needs to be displayed on the form in the client. [Translated](Translations) on the server when queried.
* `type`, the item type (see below)
* `condition`, a specific condition to display that field or not. See below for that condition format.
* `confirm`, indicating that this item should be confirmed by entering it again (such as with password fields).
* `default`, the default value to display. Should be set accordingly to the data type.
* `read_only`, indicating if a field should displayed but in a read-only state (can't be modified by the user). 
* `required`, a boolean flag indicating if the field is mandatory or not. This required flag should be checked on the client before sending the values of the form back to the server.
* `values`, if the item type is a list or a type that requires multiple values to be display, this field indicates a list of value. See below for the exact format of those values.
* `_order`, the order into which to display that particular item in that section. Lower numbers are displayed first.

### Item types
The item types indicates the type of field that needs to be displayed on the client-side. The following field types are currently defined:

* `array`: a list of items, typically displayed as a drop-down list on the client. See items values below for the format of the values to display (in the `values` field of the item).
* `audioinputs`: list of all the available audio inputs on the client
* `boolean`: a boolean value, typically displayed as a checkbox on the client.
* `checklist`: a list of items that can be all checked. This could be displayed as multiple checkbox items by the client.
* `color`: a color chooser field
* `datetime`: a date / time field.
* `duration`: a duration field, representing a time duration field.
* `hidden`: an hidden field value that should be sent with the form data but not displayed to the end-user by the client.
* `label`: a text display field which is not user-editable. If combined with the `read_only` flag, data should not be allowed to be copied from that text display field.
* `longtext`: a text field into which longer text could be entered. This should be displayed as a multi-line text box on the client.
* `numeric`: a numerical value, either decimal or floating point. Could be displayed as a text field on the client, but requires validation to ensure the field value is numeric.
* `password`: a password field. Input mask should be used with that field on the client.
* `text`: a standard text input field. Should be displayed as a short text field (1 line) on the client.
* `videoinputs`: list of all the available video inputs on the client

### Items conditions
Items conditions are operations / equations that need to be computed to find out if an item should be displayed or not. Those needs to be dynamically computed on the client when a related item is updated.

The following keys define the condition:
* `item`, the id of the item that is used to check that condition
* `op`, the operator with which to perform the check. Currently, the following values are defined: `=` (equal), `<>` (not equal), `NOT NULL` (not empty) and `CONTAINS` (item value containing the following text).
* `condition`, the condition value to compare with. Depending on the item type, this can be of various type. A special key word, `changed`, can be specified here to trigger the condition when the value was changed (or not, depending on the operator).
* `hook`, an API call (URL) to process when the condition is met. Currently, only one argument is supported, and that url should end with `=`. The client should then make the request appending the related `item` value to the query.

### Item values
Item values represents the values to be displayed in an `array` or `checklist` item types (or any other types that would require a list.

Each of the value has the following keys:
* `id`, the id of the value, which will be the data needed to be stored when sending back a filled out form to the server
* `value`, the value of the value (!), which corresponds to the text needed to be displayed on the client-side
