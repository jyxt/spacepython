from unittest import TestCase
from space import Space

__author__ = 'tesse'


class TestSpace(TestCase):

    def test_space_exist(self):
        self.assertTrue(isinstance(Space(), Space), 'Space should exist')

    def test_index_of(self):
        space = Space("Hello World")
        self.assertEqual(space.length(), 1)
        self.assertEqual(space.index_of('Hello'), 0, 'indexOf should be correct')

    def test_get_set(self):
        space = Space('Hello World')
        self.assertEqual(space.get("Hello"), 'World', 'Property should be accessible')
        self.assertEqual(type(space.get("Hello")), str, 'Leaf should be string')
        space.set('foo', 'bar')
        self.assertEqual(space.get('foo'), 'bar', 'Space should be modifiable' )

    def test_nest_space(self):
        space = Space('foobar\n one 1')
        self.assertTrue(isinstance(space.get('foobar'), Space), 'Nested space should be Space type')

    def test_key_not_exist(self):
        space = Space('foobar\n leaf 1')
        self.assertEqual(space.get('Hi'), None, 'Should return None if key does not exist')

    def test_path_not_exist(self):
        space = Space('Hello\n one 1\n two 2')
        self.assertEqual(space.get('Hello world one'), None, 'Should return None if path does not exist')

    def test_length(self):
        space = Space('list\nsingle value')
        self.assertEqual(space.length(), 2, 'space should have 2 names')  # 'name' here means 'key'
        self.assertTrue(isinstance(space.get('list'), Space), 'name without a trailing space should be name')

        # skipped a couple of tests here,  don't think can create from object literal in python

    def test_multi_line(self):
        string = 'user\n\
name Aristotle\n\
admin false\n\
stage\n\
name home\n\
domain test.test.com\n\
pro false\n\
domains\n\
 test.test.com\n\
  images\n\
  blocks\n\
  users\n\
  stage home\n\
  pages\n\
   home\n\
    settings\n\
     data\n\
      title Hello, World\n\
    block1\n\
     content Hello world\n'

        space = Space(string)
        self.assertEqual(space.get('domains test.test.com pages home settings data title'), 'Hello, World', 'Multiline creation shuold be OK')

    def test_each(self):
        space = Space('hello world\nhi mom')
        string = ''
        self.assertEqual(space.each(lambda (k, v): k), ['hello', 'hi'])
        
    def test_prepend(self):
        space = Space('hello world')
        space.prepend('first', 'word')
        self.assertEqual(space.__str__(), 'first word\nhello world\n')
        

class TestAppend(TestCase):  # haven't done the 'on append incre count' thing as in js verion
    def test_append(self):
        space = Space('hello world')
        space.append('foo', 'bar')
        space.set('foo2', 'bar')
        space.append('foo', 'two')
        self.assertEqual(space.get('foo'), 'bar')
        self.assertEqual(space.length(), 4)


class TestClear(TestCase):
    def test_clear(self):
        space = Space('Hello world')
        self.assertEqual(space.length(), 1)
        self.assertTrue(isinstance(space.clear(), Space), 'clear returns Space so chainable')
        self.assertEqual(space.length(), 0)
        
    def test_clear_with_space_argument(self):
        space = Space("Hellow world")
        space.clear("hey there")
        self.assertEqual(space.length(), 1)
        self.assertEqual(space.get('hey'), 'there', 'Clear with a Space argument should deep copy the argument Space')


class TestClone(TestCase):
    def testDeepCopy(self):
        space1 = Space('hello world')
        space2 = space1.clone()
        self.assertEqual(space2.get('hello'), 'world', 'Clone should work')
        space2.set('hello', 'mom')
        self.assertEqual(space1.get('hello'), 'world', 'Clone makes deep copy')
        space3 = space1
        space3.set('hello', 'dad')
        self.assertEqual(space1.get('hello'), 'dad', '= makes shallow copy')
        space1.set('anotherSpace', Space('123 456'))
        self.assertEqual(space3.get('anotherSpace 123'), '456')
        

class TestConcat(TestCase):
    def testConcat(self):
        space1 = Space('hi world')
        b = Space('hello there')
        space1.concat(b)
        self.assertEqual(space1.get('hello'), 'there')
        

class TestMultiline(TestCase):
    def test_multiline(self):
        space = Space('my multiline\n string')
        self.assertEqual(space.get('my'), 'multiline\nstring')
        
        space2 = Space('my \n \n multiline\n string')
        self.assertEqual(space2.get('my'), '\n\nmultiline\nstring')

        space3 = Space('brave new\n world')
        self.assertEqual(space3.get('brave'), 'new\nworld', 'ml value correct')
        self.assertEqual(str(space3), 'brave new\n world\n', 'multiline does not begin with nl')

        space4 = Space('brave \n new\n world')
        self.assertEqual(space4.get('brave'), '\nnew\nworld', 'ml begin with nl value correct')
        

class TestToStr(TestCase):
    def test__str__(self):
        space = Space("hello world")
        self.assertEqual(space.__str__(), 'hello world\n')

        # ordered
        space.set('foo', 'bar')
        self.assertEqual(space.__str__(), 'hello world\nfoo bar\n')

        # ordered
        space = Space('hello world\nline two')
        self.assertEqual(space.__str__(), 'hello world\nline two\n')


        space2 = Space('john\n age 5')
        self.assertEqual(space2.__str__(), 'john\n age 5\n')
        space2.set('multiline', 'hello\nworld')
        self.assertEqual(space2.__str__(), 'john\n age 5\nmultiline hello\n world\n')
        space2.set('other', 'foobar')
        self.assertEqual(space2.__str__(), 'john\n age 5\nmultiline hello\n world\nother foobar\n')


class TestSet(TestCase):
    def test_set(self):
        space = Space('hello world')
        self.assertEqual(space.get('hello'), 'world')
        self.assertTrue(isinstance(space.set('hello', 'mom'), Space), 'set returns self for chaining')
        
        intSpace = Space()
        intSpace.set(2, 'hi')
        self.assertEqual(intSpace.get(2), 'hi')
        
        emptyStringSpace = Space()
        emptyStringSpace.set('boom', '')
        self.assertEqual(emptyStringSpace.get('boom'), '')
        
        # this is important, value should have been changed
        self.assertEqual(space.get('hello'), 'mom')
        space.set('head style color', 'blue')
        self.assertEqual(space.get('head style color'), 'blue')


class TestHas(TestCase):
    def test_has(self):
        space = Space('hello world')
        self.assertTrue(space.has('hello'))
        self.assertFalse(space.has('world'))
