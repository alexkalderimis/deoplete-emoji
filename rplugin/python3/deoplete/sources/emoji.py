# Copyright (c) 2018 Filip Szymański. All rights reserved.
# Use of this source code is governed by an MIT license that can be
# found in the LICENSE file.

import re
import os
from contextlib import closing
import sqlite3 as sqlite

from .base import Base
from deoplete.util import load_external_module

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
DB_FILE = DIR_PATH + '/../../../../data/emoji.sqlite3.db'
QUERY = '''SELECT short_name, literal FROM emoji'''
MAX_EDITION_QUERY = '''SELECT short_name, literal FROM emoji where edition_major < ?'''

def from_row(row):
    return {'word': row[0], 'kind': ' {1} '.format(*row)}

class Source(Base):
    def __init__(self, vim):
        super().__init__(vim)

        self.__pattern = re.compile(r':[^:\s]+$')

        self.filetypes = ['gitcommit', 'markdown']
        self.mark = '[emoji]'
        self.matchers = ['matcher_length', 'matcher_full_fuzzy']
        self.name = 'emoji'
        self.max_candidates = 0
        self.vars = { 'max_emoji_edition': None }

    def gather_candidates(self, context):
        max_edition = self.get_var('max_emoji_edition')
        query = QUERY if max_edition is None else MAX_EDITION_QUERY
        params = tuple() if max_edition is None else (max_edition,)

        with closing(sqlite.connect(DB_FILE)) as conn:
            c = conn.cursor()
            return list(map(from_row, c.execute(query, params)))

    def get_complete_position(self, context):
        match = self.__pattern.search(context['input'])
        return match.start() if match is not None else -1
