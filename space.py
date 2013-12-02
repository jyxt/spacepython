__author__ = 'tesse'

import json
import re
import copy

splitInputStringPattern = re.compile(r'\n(?! )')  # newline with no space
spacePattern = re.compile(r'^([^ ]+)(\n|$)')  # not space + newline|eol
leafPattern = re.compile(r'^([^ ]+) ')  # not space + one space


class Space:

    """
    Space is key : value pair where key is string and
    value is either string or another Space object
    """

    def __init__(self, content=None):
        self.__data = []
        self.__events = {}
        if content:
            self.__load(content)

    def __load(self, content):
        if isinstance(content, basestring):
            self.__load_from_string(content)
        elif isinstance(content, Space):
            self.__data = copy.deepcopy(content._Space__data)  # not the best way to do it
        else:
            raise NotImplementedError('currently can only instantiate from string and Space object')

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

    def __set_data(self, key, value, index=None, overwrite=False):
        if index is None:  # can't use if not index here cuz python eval 0 to False
            self.__data.append((key, value))
        elif overwrite:
            self.__data[self.index_of(key)] = (key, value)
        else:
            self.__data.insert(index, (key, value))


    def __get_value_by_key(self, key):
        return next((v for k, v in self.__data if k == key), None)

    def __get_value_by_string(self, string):
        if not string:
            raise ValueError("input string can't be empty")

        # added check if xpath for earlier return
        if not Space.is_xpath(string):
            return self.__get_value_by_key(string)

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

    def get(self, content):
        content = str(content)
        return self.__get_value_by_string(content)

    def set(self, key, value, index=None):
        key = str(key)
        if Space.is_xpath(key):
            self.__set_value_by_path(key, value)
        elif self.has(key):
            print self.index_of(key)
            self.__set_data(key, value, index=self.index_of(key), overwrite=True)
        else:
            self.__set_data(key, value, index=index)
        # TODO: add trigger
        return self

    def __set_value_by_path(self, path, value):  # called setByXPath in js version
        if path is None:
            return None  # return null in js version
        keys = str(path).split(' ')
        context = self
        isLeaf = lambda index: index == len(keys) - 1
        for index, key in enumerate(keys):

            if not isLeaf and isinstance(context.__get_value_by_key(key), Space):
                context = context.get(key)
                continue

            if index == (len(keys)-1):
                new_val = value
            else:
                new_val = Space()

            if context.has(key):
                context.__set_data(key, new_val, index=context.index_of(key), overwrite=True)
            else:
                context.__set_data(key, new_val)
            context = context.get(key)
        return self


    @staticmethod
    def is_xpath(content):
        return ' ' in content

    # misc

    def has(self, key):
        return self.__get_value_by_key(key) is not None

    def __clear(self):
        self.__data = []
        return self

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
            elif '\n' in value.__str__():
                string += ' ' + value.replace('\n', ('\n' + ' '*(spaces + 1))) + '\n'
            else:
                string += ' ' + value + '\n'

        return string

    # ordered operations
    def each(self, fn):
        """
        fn should take one argument (k,v),
        different from js version
        """
        return map(fn, self.__data)

    def append(self, key, value):
        self.__data.append((key, value))

    def prepend(self, key, value):
        self.__data.insert(0, (key, value))

    def concat(self, b):
        if isinstance(b, basestring):
            b = Space(b)
        self.__data.extend(b._Space__data)
        return self

    def create(self, k, v):
        self.__data.append([k, v])

    # observer
    def on(self, event, callback):  # doesn't check if duplicate events?
        if event not in self.__events:
            self.__events[event] = []
        self.__events[event].append(callback)

    def off(self, event, callback):
        if event not in self.__events:
            return None
        try:
            index = self.__events[event].index(callback)
            del self.__events[event][index]
        except ValueError:
            return None

    def trigger(self, event, *args):
        if event not in self.__events:
            return None
        for callback in self.__events[event]:
            print 'triggered ' + event
            callback(*args)



if __name__ == '__main__':
    space = Space('name John\nage\nfavoriteColors\n blue\n  blue1 1\n  blue2 2\n green\n red 1\n')


    print space.to_json()

    print space
    print space.set('favoriteColors blue', 'aaa')




