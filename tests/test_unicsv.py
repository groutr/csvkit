#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cStringIO import StringIO
import csv
import os
import unittest

from csvkit import unicsv

class TestUnicodeCSVReader(unittest.TestCase):
    def test_utf8(self):
        with open('examples/test_utf8.csv') as f:
            reader = unicsv.UnicodeCSVReader(f, encoding='utf-8')
            self.assertEqual(reader.next(), ['a', 'b', 'c'])
            self.assertEqual(reader.next(), ['1', '2', '3'])
            self.assertEqual(reader.next(), ['4', '5', u'ʤ'])

    def test_latin1(self):
        with open('examples/test_latin1.csv') as f:
            reader = unicsv.UnicodeCSVReader(f, encoding='latin1')
            self.assertEqual(reader.next(), ['a', 'b', 'c'])
            self.assertEqual(reader.next(), ['1', '2', '3'])
            self.assertEqual(reader.next(), ['4', '5', u'©'])

    def test_utf16_big(self):
        with open('examples/test_utf16_big.csv') as f:
            reader = unicsv.UnicodeCSVReader(f, encoding='utf-16')
            self.assertEqual(reader.next(), ['a', 'b', 'c'])
            self.assertEqual(reader.next(), ['1', '2', '3'])
            self.assertEqual(reader.next(), ['4', '5', u'ʤ'])

    def test_utf16_little(self):
        with open('examples/test_utf16_little.csv') as f:
            reader = unicsv.UnicodeCSVReader(f, encoding='utf-16')
            self.assertEqual(reader.next(), ['a', 'b', 'c'])
            self.assertEqual(reader.next(), ['1', '2', '3'])
            self.assertEqual(reader.next(), ['4', '5', u'ʤ'])

class TestUnicodeCSVWriter(unittest.TestCase):
    def test_utf8(self):
        output = StringIO()
        writer = unicsv.UnicodeCSVWriter(output, encoding='utf-8')
        self.assertEqual(writer._eight_bit, True)
        writer.writerow(['a', 'b', 'c'])
        writer.writerow(['1', '2', '3'])
        writer.writerow(['4', '5', u'ʤ'])

        written = StringIO(output.getvalue())

        reader = unicsv.UnicodeCSVReader(written, encoding='utf-8')
        self.assertEqual(reader.next(), ['a', 'b', 'c'])
        self.assertEqual(reader.next(), ['1', '2', '3'])
        self.assertEqual(reader.next(), ['4', '5', u'ʤ'])

    def test_latin1(self):
        output = StringIO()
        writer = unicsv.UnicodeCSVWriter(output, encoding='latin1')
        self.assertEqual(writer._eight_bit, True)
        writer.writerow(['a', 'b', 'c'])
        writer.writerow(['1', '2', '3'])
        writer.writerow(['4', '5', u'©'])

        written = StringIO(output.getvalue())

        reader = unicsv.UnicodeCSVReader(written, encoding='latin1')
        self.assertEqual(reader.next(), ['a', 'b', 'c'])
        self.assertEqual(reader.next(), ['1', '2', '3'])
        self.assertEqual(reader.next(), ['4', '5', u'©'])

    def test_utf16_big(self):
        output = StringIO()
        writer = unicsv.UnicodeCSVWriter(output, encoding='utf-16-be')
        self.assertEqual(writer._eight_bit, False)
        writer.writerow(['a', 'b', 'c'])
        writer.writerow(['1', '2', '3'])
        writer.writerow(['4', '5', u'ʤ'])

        written = StringIO(output.getvalue())

        reader = unicsv.UnicodeCSVReader(written, encoding='utf-16-be')
        self.assertEqual(reader.next(), ['a', 'b', 'c'])
        self.assertEqual(reader.next(), ['1', '2', '3'])
        self.assertEqual(reader.next(), ['4', '5', u'\u02A4'])

    def test_utf16_little(self):
        output = StringIO()
        writer = unicsv.UnicodeCSVWriter(output, encoding='utf-16-le')
        self.assertEqual(writer._eight_bit, False)
        writer.writerow(['a', 'b', 'c'])
        writer.writerow(['1', '2', '3'])
        writer.writerow(['4', '5', u'ʤ'])

        written = StringIO(output.getvalue())

        reader = unicsv.UnicodeCSVReader(written, encoding='utf-16-le')
        self.assertEqual(reader.next(), ['a', 'b', 'c'])
        self.assertEqual(reader.next(), ['1', '2', '3'])
        self.assertEqual(reader.next(), ['4', '5', u'\u02A4'])

class TestUnicodeCSVDictReader(unittest.TestCase):
    def setUp(self):
        self.f = open('examples/dummy.csv')

    def tearDown(self):
        self.f.close()

    def test_reader(self):
        reader = unicsv.UnicodeCSVDictReader(self.f)

        self.assertEqual(reader.next(), {
            u'a': u'1',
            u'b': u'2',
            u'c': u'3'
        })

class TestUnicodeCSVDictWriter(unittest.TestCase):
    def setUp(self):
        self.output = StringIO()

    def tearDown(self):
        self.output.close()

    def test_writer(self):
        writer = unicsv.UnicodeCSVDictWriter(self.output, ['a', 'b', 'c'], writeheader=True)
        writer.writerow({
            u'a': u'1',
            u'b': u'2',
            u'c': u'☃'
        })

        result = self.output.getvalue()

        self.assertEqual(result, 'a,b,c\r\n1,2,☃\r\n')

class TestMaxFieldSize(unittest.TestCase):
    def setUp(self):
        self.lim = csv.field_size_limit()

        with open('dummy.csv', 'w') as f:
            f.write('a' * 10)
            f.close()

    def tearDown(self):
        # Resetting limit to avoid failure in other tests.
        csv.field_size_limit(self.lim)
        os.system('rm dummy.csv')

    def test_maxfieldsize(self):
        # Testing --maxfieldsize for failure. Creating data using str * int.
        with open('dummy.csv', 'r') as f:
            c = unicsv.UnicodeCSVReader(f, maxfieldsize=9)
            try:
                c.next()
            except unicsv.FieldSizeLimitError:
                pass
            else:
                raise AssertionError('Expected unicsv.FieldSizeLimitError')

        # Now testing higher --maxfieldsize.
        with open('dummy.csv', 'r') as f:
            c = unicsv.UnicodeCSVReader(f, maxfieldsize=11)
            self.assertEqual(['a' * 10], c.next())

