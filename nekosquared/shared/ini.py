"""
Basic implementation of an INI file parser. This is for very basic rudimentary
configuration files.

Supports dicts and dict of dicts. Keys and values are treated as strings
and may be quoted in double quotes. No escape sequences are currently
implemented other than ``\"`` and `\\`, and these are only used if the string
is quoted.

Sections are supported by placing the identifier in ``[]`` square parenthesis.

Lines starting with `;` are treated as comments.

https://en.wikipedia.org/wiki/INI_file
"""
import re


__assign_re = re.compile(r'^([^=]+) ?= ?(.+)$')
__section_re = re.compile(r'^\[([^\n=]+)\]$')


def __parse_quotes(token):
    """Takes a section and if it is quoted, we parse the quoted section."""
    token = token.strip()

    # Ignore if not a quoted string.
    if not token or len(token) == 1 or not token[0] == token[-1] == '"':
        return token
    else:
        string = ''
        i = 1
        while i < len(token) - 1:
            current = token[i:]
            if current.startswith('\\"'):
                i += 2
                string += '"'
            elif current.startswith('\\r'):
                i += 2
                string += '\r'
            elif current.startswith('\\n'):
                i += 2
                string += '\n'
            elif current.startswith('\\\\'):
                i += 2
                string += '\\'
            else:
                i += 1
                string += current[0]

        if string.isdigit():
            return int(string)
        else:
            return string


def load(fp):
    """
    Reads the INI file.
    :param fp: the stream to read from.
    :return: a dict of all key-value pairs read from file.
    """
    # Read the lines into the data.
    data = fp.readlines()
    nested_dict = None

    result = {}

    def insert(k, v):
        if nested_dict is None:
            result[k] = v
        else:
            result[nested_dict][k] = v

    for i, line in enumerate(data):
        line = line.strip()

        # Ignore comments and empty lines.
        if not line or line.startswith(';'):
            continue

        section = __section_re.findall(line)
        assign = __assign_re.findall(line)

        assert not all((section, assign)), 'Your regex is broken.'

        if section:
            nested_dict = section.pop()
            result[nested_dict] = {}
        elif assign:
            try:
                key, value = assign.pop()
            except ValueError:
                raise SyntaxError(f'Line {i + 1} is invalid: {line!r}')
            key, value = __parse_quotes(key), __parse_quotes(value)
            insert(key, value)
        else:
            raise SyntaxError(f'Unexpected token on line {i + 1}: {line!r}')

    return result
