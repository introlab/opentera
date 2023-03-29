# Translations
OpenTera uses [Flask-Babel](https://python-babel.github.io/flask-babel/) to translate the various API messages. Each
[core services](../services/OpenTera_Services) has an associated portable object file (.po) containing the text 
translations. 

While it could have been possible to uses specific keys throughout the code for each string that needed to be 
translated, it was decided to write each string as a textual English text and then translate from that English text to
a localized text. This has the advantage of making code more readable and easier to write (without having to refer to
a dictionary), but has the disadvantage of having to redo some translations if the underlying text changes.

Each translation file can be found in the related service `translations` folder, with a sub folder for each language
(such a `en` for English and `fr` for French). The [core TeraServer service](../services/teraserver/teraserver.rst)
has its translations in [this path](https://github.com/introlab/opentera/tree/main/teraserver/python/translations).

## Client translation selection
Client can select the server response language by setting the `Accept-Language` value in the request header. Fallback
will occurs in English if the selected language is not valid (no translation existing for this language) or if that 
header value is not found in the request.

By default, browsers will set this field automatically, so any web-based application will be correctly localized. It
is however possible to change that value manually and to set it, as required, if other client are used.

## Creating/editing translations
An integration with the [cmake](https://cmake.org/) script is done to automatically runs the `pybabel` utility and 
extract all the strings to translate in the services. By running `cmake` with one of the target ending with the 
`translations` keyword, all strings encapsulated with the `gettext` function will be detected, and the translation 
file (.po) will be updated accordingly.

Each of the .po file can be manually edited in a text editor to update the translation, but a tool such as
[PoEdit](https://poedit.net/) is suggested to ease the translation process.

## Compiling/generating translations
OpenTera will use a compiled translation file (.mo). It is possible to manually generates such a file, but the `cmake`
integration will also automatically generates such a translation when selecting a target ending with the 
`translations` keyword.
