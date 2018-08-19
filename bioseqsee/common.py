#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import time

from datetime import datetime
from collections import Iterable

if sys.version_info.major < 3:
    FileHandle = file
else:
    import io
    FileHandle = io.IOBase


RESET_ALL   = '\x1b[0m'

BRIGHT      = '\x1b[1m'
DIM         = '\x1b[2m'
ITALIC      = '\x1b[3m'
UNDERSCORED = '\x1b[4m'
BACKGROUND  = '\x1b[7m'
NORMAL      = '\x1b[22m'

BLACK       = '\x1b[30m'
RED         = '\x1b[31m'
GREEN       = '\x1b[32m'
YELLOW      = '\x1b[33m'
BLUE        = '\x1b[34m'
MAGENTA     = '\x1b[35m'
CYAN        = '\x1b[36m'
WHITE       = '\x1b[37m'
RESET_COLOR = '\x1b[39m'


class newstring(str):
    
    def add_color_and_style(self, color=CYAN, style=NORMAL):
        # type: (self, str, str) -> newstring
        '''
        Get a new string with the given color and style from the original.
        Return a cyan normal-style string by default.
    
        @param: color 
        @param: style 
        
        @return: a newstring colored and styled 
        '''
        return newstring(color + style + self + RESET_ALL)
    
    
    def check_delimiter(self, priority=(';', ',', '|')):
        # type: (self, Iterable) -> str or None
        '''
        In an annotation file, the value in each column are often 
        delimited by symbols like ';', ',', or '|'. This function 
        is for finding the proper delimiter in the given string.
    
        @param: string   -- The input string for checking
        @param: priority -- An iterable of candidate symbols 
                            with priority. 
                            Notice: The order of the symbols 
                            matters. e.g. if both ';' and ',' 
                            are in the input string, return 
                            ';' rather than ',' by default.
    
        @return:            A proper symbol as the delimiter, 
                            or ``None`` if nothing found.
        '''
        for mark in priority:
            if mark in string:
                return mark
        return None
    
    
    def strip(self, pattern, position='a'):
        # type: (self, str, str) -> newstring
        '''
        Remove the pattern as a whole from the start or the end 
        or both the start and the end of the input string.
    
        @param: string   -- The input string to deal with.
        @param: pattern  -- The prefix or the suffix you want 
                            to remove from the input string. 
                            The type should be a string.
        @param: position -- Input 'l' if lstrip, or 'r' if 
                            rstrip, or 'a' if you need both ends.
                            Default: 'a'.
        '''
        if not isinstance(pattern, str):
            raise TypeError('The arguments should be a string!')
        
        if position == 'a':
            return self.lstrip(pattern).rstrip(pattern)
        elif position == 'l':
            return self.lstrip(pattern)
        elif position == 'r':
            return self.rstrip(pattern)
    
    
    def lstrip(self, pattern):
        # type: (self, str) -> newstring
        while self.startswith(pattern):
            self = newstring(self[len(pattern):])
        return self
    
    
    def rstrip(string, pattern):
        # type: (self, str) -> newstring
        while self.endswith(pattern):
            self = newstring(self[:-len(pattern)])
        return self
    

def check_title(fileobj, spec_names=(), comeback=False, 
                min_col_num=3, header_mark='#'):
    # type: (FileHandle, Iterable, bool, int, str) -> dict
    '''
    Check the indices of column names in the given file object of 
    a tab-delimited file (either a VCF file or a TSV file is ok).
    
    Notice: Here we will choose the first line with at least 3 (or 
    other given numbers) tab-separated values as the title line.

    @param: fileobj      -- The ``file object`` for the title checking

    @param: spec_names   -- Specific names you need to check in the title. 
                            You can use '.*' for uncertain strings.

    @param: comeback     -- If the file pointer should go back to the 
                            original position after the title checking, 
                            choose comeback=True (default: False)
    
    @param: min_col_num  -- Choose the first line with at least 
                            N tab-separated values as the title 
                            line. 
                            The number N is given by the param 
                            min_col_num (default: 3).
    @param: header_mark  -- The remark symbol of the header lines 
                            -- a hash ('#') symbol by default.
                            
                            In fact, the function will take the first 
                            line with a column number not less than 3 
                            (no matter whether the line starts with a 
                            header mark or not), and the lines above 
                            it with a header mark as the header lines.

    @return: title       -- A dict with the column names as 
                            keys and the indices as values.
                            e.g. {'.len': 3, 
                                  '.Column_Names': ['Name', 'Age', 'Gender'], 
                                  '.column_names': ['name', 'age', 'gender'], 
                                  '.samples': [], 
                                  '.header': 'Name\tAge\tGender\n', 
                                  'Name': 0, 'Age': 1, 'Gender': 2, 
                                  'name': 0, 'age': 1, 'gender': 2
                                 }
                            Notice: 
                                Both the original column names and the 
                            lowercase strings of column names are used 
                            as keys. 

                                There are several additional keys storing 
                            special corresponding values:
                            '.len' => 
                                  the length of the columns, 
                            '.Column_Names' => 
                                  the list of the column names, 
                            '.column_names' => 
                                  the list of the lowercase column names, 
                            '.samples' => 
                                  the list of the sample names in a VCF file, 
                            '.header' => 
                                  the content of the header lines.

    Cautions for developers: 
        DO NOT USE a for loop when you need the value of fileobj.tell() -- a 
    for loop in reading files seems to read lines one by one BUT IT DOES NOT! 
    A for loop reads a bulk of characters each time. USE A WHILE LOOP.
    '''
    # 0. Initialize: 
    title = {'.len': int(),           # for the number of the columns
             '.Column_Names': list(), # for the names of the columns
             '.column_names': list(), # for the lower-case of the column names
             '.samples': list(),      # for the names of the samples   
             '.header': str()         # for the string of the header line(s)
            }
    ori_pos = 0
    try:
        ori_pos = fileobj.tell()
        fileobj.seek(0, 0)
    except IOError:
        pass
    # 1. Find the first line with at least 3 (or the given number) columns: 
    List = []
    while len(List) < min_col_num and List != ['']:
        line = fileobj.readline()
        List = line.rstrip('\n').lstrip(header_mark).split('\t')
        list_lower = [i.lower().strip() for i in List] # lower() and strip()
        if line.startswith(header_mark):
            title['.header'] += line
    # 2. Check if there are lines starting with a header mark beneath:
    try:
        pos = fileobj.tell()
        line = fileobj.readline()
        while line.startswith(header_mark):
            title['.header'] += line
            pos = fileobj.tell()
            line = fileobj.readline()
        fileobj.seek(pos, 0)
    except IOError:
        pass
    # 3. Update the dict 'title':
    if List != ['']:
        title['.header'] += line
        title['.len'] = len(List)
        title['.Column_Names'] = List
        title['.column_names'] = list_lower
    for L in (List, list_lower):
        title.update({column: L.index(column) for column in L 
                                              if column.strip()})
    # 4. Find the indices of the annotations 
    #    which starts with the following strings:
    '''
    specific_names  =  ('chr', 
                        'avsnp', 
                        'gencode', 
                        'clinvar', 
                        '1000g.*_all', 
                        '1000g.*_eas', 
                        '1000g.*_chinese', 
                        'esp6500.*_all', 
                        'novodb_wes', 
                        'novodb_wgs', 
                        'gerp', 
                        'dbscsnv', 
                        'interpro', 
                        'format', 
                        'ori_ref', 
                        'alt_count', 
                        'ref_count')
    '''
    for name in spec_names:
        title[name] = None
        for column in list_lower:
            if re.match(name, column):
                title[name] = list_lower.index(column)
                break
    # 5. Find the indices of the samples to the right of the FORMAT column:
    try:
        if title['format'] and title['ori_ref']:
            for i in range(title['format'] + 1, title['ori_ref']):
                title['.samples'].append(List[i])
        elif title['format']:
            for i in range(title['format'] + 1, len(List)):
                title['.samples'].append(List[i])
    except KeyError:
        pass
    # 6. Check if the file pointer is needed to go back:
    if ori_pos != 0 and comeback:
        fileobj.seek(ori_pos, 0)
    return title


def cmdExists(cmd):
    # type: (str, ) -> bool

    # The function is copied from the software "poreFUME".
    # The MIT License (MIT) Copyright (c) 2016 Eric van der Helm.
    '''
    Check if the given command exists in the environment PATH.
    '''
    return any(
        os.access(os.path.join(path, cmd), os.X_OK)
        for path in os.environ['PATH'].split(os.pathsep)
    )


def current_time(format='%Y%m%d'):
    # type: (str, ) -> str
    '''
    Get the current date and time using datetime.datetime.now().

    @param: format -- The format for datetime.datetime.now().strftime()

    '''
    return datetime.now().strftime(format)


def mkdir(path, warning=False):
    # type: (str, bool) -> int
    '''
    Make a new directory and:
        a) create all the intermediate directories as required; 
        b) without OSError/FileExistsError if it already exists.

    @param: path    -- Path to the new directory you want to make
    @param: warning -- Set to True if you need warnings into STDERR

    @return: exitcode -- If the new directory is made 
                            successfully, return 0.
                         If the directory already exists, return 1.
    '''
    if not os.path.exists(path):
        os.makedirs(path)
        return 0
    else:
        if warning:
            sys.stderr.write(
                '[WARNING] {} already exists!\n'.format(path))
        return 1


