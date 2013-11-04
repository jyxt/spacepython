__author__ = 'tesse'

import json
import re
import copy

splitInputStringPattern = re.compile('\n(?! )')  # newline with no space
spacePattern = re.compile('^([^ ]+)(\n|$)')  # not space + newline|eol
leafPattern = re.compile('^([^ ]+) ')  # not space + one space


class Space:

    def __init__(self, content=None):
        self.__data = []
        if content:
            self.__load(content)

    def __load(self, content):
        if isinstance(content, basestring):
            self.__load_from_string(content)
        elif isinstance(content, Space):
            self.__data = copy.deepcopy(content._Space__data)  # not the best way to do it

    def __load_from_string(self, string):

        # remove leading spaces
        string = string.lstrip()
        # remove windows \r
        string = string.replace('\n\r', '\n').replace('\r\n', '\n')
        # remove trailing newline(s)
        string = string.rstrip('\n')
        # TODO: add windows strip \r

        spaces = splitInputStringPattern.split(string)

        for space in spaces:
            spaceMatch = spacePattern.search(space)
            if spaceMatch:
                match = spaceMatch.groups()[0]  # returns
                print spaceMatch.groups()[1]
                self.__set_data(match, Space(space[len(match):].replace('\n ', '\n')))
            elif leafPattern.search(space):
                match = leafPattern.search(space).groups()[0]
                self.__set_data(match, space[len(match)+1:].replace('\n ', '\n'))

    def __set_data(self, key, value):
        # if exist then replace otherwise append
        if self.has(key):
            self.__data[self.index_of(key)] = (key, value)
        else:
            self.__data.append((key, value))

    def append(self, key, value):
        self.__data.append((key, value))

    def __get_value_by_key(self, key):
        # [v for k, v in self.__data if k == key]  # returns a list values with matching key
        return next((v for k, v in self.__data if k == key), None)

    def __get_value_by_string(self, string):
        if not string:
            raise ValueError("input string can't be empty")
        string = string.strip()  # remove leading and trailing whitespace

        # single entry, return from __data[key]
        if " " not in string:
            return self.__get_value_by_key(string)

        # convert multiple spaces to single space
        string = ' '.join(string.split())

        # pop first entry, recursion
        first, separator, rest = string.partition(' ')
        firstValue = self.__get_value_by_key(first)

        # if first key has non-None value
        if firstValue:
            return firstValue.__get_value_by_string(rest)

        # TODO: verify get, set input types
    def get(self, content):
        return self.__get_value_by_string(content)

    def set(self, path, value):
        if path and value:
            path = str(path)
            return self.__set_value_by_path(path, value)

    def __set_value_by_path(self, path, value):
        if " " not in path:
            self.__set_data(path, value)
            return self  # for chanining
        path = ' '.join(path.split())
        first, separator, rest = path.partition(' ')
        return self.__get_value_by_key(first).__set_value_by_path(rest, value)

    # TODO:
    def is_xpath(self, content):
        return

    # misc

    def has(self, key):
        if self.__data:
            return key in zip(*self.__data)[0]

    def __clear(self):
        self.__data = []

    def clear(self, string=None):
        self.__clear()
        if string:
            self.__load(string)
        return self

    def clone(self):
        return copy.deepcopy(self)

    def length(self):
        return len(self.__data)

    def get_keys(self):
        return zip(*self.__data)[0]

    def index_of(self, key=None):
        if key and self.has(key):
            return self.get_keys().index(key)

    # JSON
    def jsonable(self):
        return dict(self.__data)  # just convert it to dict, since JSON is unordered

    def to_json(self):
        return self.SpaceEncoder().encode(self)

    class SpaceEncoder(json.JSONEncoder):

        def default(self, o):
            if isinstance(o, Space):
                return o.jsonable()
            return json.JSONEncoder.default(self, o)

    def __str__(self):
        return self.__str_helper(0)

    def __str_helper(self, spaces):
        string = ''

        if not self.__data:
            return ''

        for key, value in self.__data:
            string += ' '*spaces + key  # equivalent of Space.strRpeat in js code
            if isinstance(value, Space):
                string += '\n' + value.__str_helper(spaces + 1)
    #        elif value == '':
     #           string += ' \n'
            elif '\n' in value.__str__():
                string += ' ' + value.replace('\n', ('\n' + ' '*(spaces + 1))) + '\n'
            else:
                string += ' ' + value + '\n'

        return string


if __name__ == '__main__':
    space = Space('name John\n age\nfavoriteColors\n blue\n green\n red 1\n')
    print space.to_json()

    print space








