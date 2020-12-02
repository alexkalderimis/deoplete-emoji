#!/usr/bin/env python3

# Copyright (c) 2018 Filip Szymański and 2020 Alex Kalderimis. All rights reserved.
# Use of this source code is governed by an MIT license that can be
# found in the LICENSE file.

import re
import urllib.request
import sqlite3 as sqlite
import os 
import locale

URL = 'https://unicode.org/Public/emoji/13.1/emoji-test.txt'
PATTERN = re.compile(''.join([
    r'^',
    r'(?P<code_points>([0-9A-F]{4,5} ?)+)',
    r'\s+;\s+',
    r'(?P<status>(fully-qualified|minimally-qualified|unqualified))',
    r'\s+#\s+',
    r'(?P<literal>\S+)',
    r'\s+',
    r'E(?P<edition_major>\d+)\.(?P<edition_minor>\d+)',
    r'\s+',
    r'(?P<short_name>.+)']))

dir_path = os.path.dirname(os.path.realpath(__file__))
db_path = dir_path + '/../data/emoji.sqlite3.db'

def create_table(c):
    c.execute('''
    CREATE TABLE emoji (
        code_points text,
        status text,
        literal text,
        short_name text,
        edition_major integer,
        edition_minor integer
    )
    ''')

def fetch_text():
    with urllib.request.urlopen(URL) as f:
        return f.read().decode('utf-8')

def rows(lines):
    for line in lines:
        m = PATTERN.match(line)

        if m:
            short_name = ':{0}:'.format(re.sub(r'[:\s]+', '_', m.group('short_name')))
            major = locale.atoi(m.group('edition_major'))
            minor = locale.atoi(m.group('edition_minor'))
            yield (m.group('code_points'), m.group('status'), m.group('literal'), short_name, major, minor)

if __name__ == '__main__':
    print('Opening {0} for writing'.format(db_path))

    conn = sqlite.connect(db_path)
    c = conn.cursor()
    create_table(c)

    text = fetch_text()

    for row in rows(text.splitlines(0)):
      c.executemany('INSERT INTO emoji VALUES (?, ?, ?, ?, ?, ?)', [row])

    conn.commit()
    conn.close()
