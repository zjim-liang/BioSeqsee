# -*- coding: utf-8 -*-
from collections import Iterable


def chr2int(chrom):
    # type: (str or int, ) -> int
    '''
    Convert a chromosome (of str or int type) to an integer.
    The chromosomes X, Y, and MT will be 23, 24, and 25, respectively.
    '''
    if isinstance(chrom, str):
        chrom = chrom.strip().lstrip('chr')
        if chrom == 'X':
            return 23
        elif chrom == 'Y':
            return 24
        elif chrom.upper() in ['M', 'MT', 'MITO', 'MITOCHONDRIA']:
            return 25
        elif chrom.upper() == 'HSCHR6_MHC_COX':
            return 6
        elif '_' in chrom:
            chrom = chrom.split('_')[0]
    try:
        if 0 < int(chrom) < 26:
            return int(chrom)
        else:
            raise ValueError('invalid literal for a chromosome: '
                             + repr(chrom))
    except ValueError:
        raise ValueError('invalid literal for a chromosome: '
                         + repr(chrom))


def chr2norm(chrom, convention=('hg19', 'b37')[1]):
    # type: (str or int, str) -> str
    chrom = chr2int(chrom)
    if convention == 'b37':
        return int_to_b37chr(chrom)
    elif convention == 'hg19':
        return int_to_hg19chr(chrom)
    else:
        raise AssertionError('[ERROR] an invalid convention'
                             ' for the chromosome notation.')


def hg19chr_to_b37chr(chrom):
    # type: (str, ) -> str
    if '_' not in chrom:
        chrom = chrom.lstrip('chr')
        if chrom == 'M':
            return 'MT'
        elif chrom in ['X', 'Y']:
            return chrom
        else:
            try:
                chrom = int(chrom)
            except ValueError:
                raise ValueError('[ERROR] An invalid chromosome:'
                                 ' "{}"'.format(chrom))
            if 0 < chrom < 23:
                return str(chrom)
            else:
                raise ValueError('[ERROR] An invalid chromosome:'
                                 ' "{}"'.format(chrom))
    else:
        raise AssertionError('The function is under construction!')


def int_to_b37chr(chrom):
    # type: (int, ) -> str
    '''
    Convert an integer to the b37-style chromosome notation.
    '''
    if 0 < chrom < 23:
        return str(chrom)
    elif chrom == 23:
        return 'X'
    elif chrom == 24:
        return 'Y'
    elif chrom == 25:
        return 'MT'
    else:
        raise ValueError('[ERROR] the input was not a chromosome!')


def int_to_hg19chr(chrom):
    # type: (int, ) -> str
    '''
    Convert an integer to the UCSC hg19-style chromosome notation.
    '''
    if 0 < chrom < 23:
        return 'chr' + str(chrom)
    elif chrom == 23:
        return 'chrX'
    elif chrom == 24:
        return 'chrY'
    elif chrom == 25:
        return 'chrM'
    else:
        raise ValueError('[ERROR] the input was not a chromosome!')


class Bed(object):
    '''
    To get a Bed object recording a genomic feature track:
    
    Bed() -> new null object
    Bed('1\\t10000\\t20000') -> Bed('1', 10000, 20000)
    Bed(['10000', '20000']) -> Bed(None, 10000, 20000)
    Bed(['chr1', '10000', '20000', '+']) -> Bed('1', 10000, 20000, '+')
    '''
    def __init__(self, obj='', warning=False):
        # type: (self, str or Iterable, bool) -> None
        self.__bed = tuple()
        self.chrom = None
        self.start = None
        self.end = None
        #
        if isinstance(obj, str):
            splitted = obj.rstrip('\n').split()
        elif isinstance(obj, Iterable):
            splitted = obj
        else:
            Bed.raise_input_error()
        #
        if len(splitted) == 0:
            return
        elif len(splitted) == 2:
            try:
                start = int(splitted[0])
                end = int(splitted[1])
            except ValueError:
                Bed.raise_input_error()
            if 0 < start < 30 and warning:
                sys.stderr.write('[WARN] The start coordinate is "{}".'
                                 ' Be careful if you input'
                                 ' "chr\tcoordinate"!\n'.format(start))
        elif len(splitted) > 2:
            try:
                start = int(splitted[1])
                end = int(splitted[2])
            except ValueError:
                Bed.raise_input_error()
            self.chrom = chr2norm(splitted[0])
        else:
            Bed.raise_input_error()
        #
        self.start = start
        self.end = end
        self.__bed = (self.chrom, self.start, self.end) + tuple(splitted[3:])
        return
        
    def __iter__(self):
        return iter(self.__bed)

    def __bool__(self):
        return bool(self.__bed)

    def __nonzero__(self):
        return self.__bool__()

    def __str__(self):
        if self.__bed:
            return "Bed({}, {}, {}{})".format(
                None if self.chrom is None else "'{}'".format(self.chrom), 
                self.start, 
                self.end, 
                ', '.join(self.__bed[3:])
            )
        else:
            return "Bed()"

    def __repr__(self):
        return '<{}.{} object at {}>'.format(
            self.__class__.__module__,
            self.__class__.__name__,
            hex(id(self))
        )
        
    @staticmethod
    def raise_input_error(self):
        raise ValueError('[ERROR] the input cannot be'
                         ' converted to a Bed object!')


def mergeBed(Beds):
    # type: (Iterable, ) -> Iterable
    pass


def sortBed(Beds):
    # type: (Iterable, ) -> Iterable
    pass


