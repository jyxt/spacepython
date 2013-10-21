__author__ = 'tesse'

import json
import re
import copy


splitInputStringPattern = re.compile('\n(?! )')  # newline with no space
spacePattern = re.compile('^([^ ]+)(\n|$)')  # not space + newline|eol
leafPattern = re.compile('^([^ ]+) ')  # not space + one space


class Space:

    def __init__(self, content=None):
        self.__data = {}
        if content:
            self.__load(content)

    def __load(self, content):
        if isinstance(content, basestring):
            self.__loadFromString(content)
        elif isinstance(content, Space):
            # this works but not great to call jsonable
            self.__data = copy.deepcopy(content.jsonable())

    def __loadFromString(self, string):

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
                self.__setData(match, Space(space[len(match):].replace('\n ', '\n')))
            elif leafPattern.search(space):
                match = leafPattern.search(space).groups()[0]
                self.__setData(match, space[len(match)+1:].replace('\n ', '\n'))

    def __setData(self, key, value):
        self.__data[key] = value

    def __getValueByKey(self, key):
        if key in self.__data.keys():
            return self.__data[key]

    def __getValueByString(self, string):
        if not string:
            raise ValueError("input string can't be empty")
        string = string.strip()  # remove leading and trailing whitespace

        # single entry, return from __data[key]
        if " " not in string:
            return self.__getValueByKey(string)

        # convert multiple spaces to single space
        string = ' '.join(string.split())

        # pop first entry, recursion
        first, separator, rest = string.partition(' ')
        firstValue = self.__getValueByKey(first)

        # if first key has non-None value
        if firstValue:
            return firstValue.__getValueByString(rest)

        # TODO: verify get, set input types
    def get(self, content):
        return self.__getValueByString(content)

    def set(self, path, value):
        if path and value:
            path = str(path)
            return self.__setValueByPath(path, value)

    def __setValueByPath(self, path, value):
        if " " not in path:
            self.__setData(path, value)
            return self  # for chanining
        path = ' '.join(path.split())
        first, separator, rest = path.partition(' ')
        return self.__getValueByKey(first).__setValueByPath(rest, value)



    # TODO:
    def isXpath(self, content):
        return

    # misc

    def __clear(self):
        self.__data.clear()

    def clear(self, string=None):
        self.__clear()
        if string:
            self.__load(string)
        return self

    def clone(self):
        return copy.deepcopy(self)

    def length(self):
        return len(self.__data)

    def getKeys(self):
        return self.__data.keys()

    def indexOf(self, key=None):
        if key:
            return self.getKeys().index(key)

    # JSON
    def jsonable(self):
        return self.__data

    def toJSON(self):
        return self.SpaceEncoder().encode(self)

    class SpaceEncoder(json.JSONEncoder):

        def default(self, o):
            if isinstance(o, Space):
                return o.jsonable()
            return json.JSONEncoder.default(self, o)


if __name__ == '__main__':
    space = Space('a\n b\naa 11\n')
    s2 = Space('name John\nage 29\nfavoriteColors\n blue\n green\n red 1\n')

    ss = Space('name John age 29 favoriteColors blue green red')
    print ss.toJSON()








