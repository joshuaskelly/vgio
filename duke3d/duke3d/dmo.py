"""This module provides file I/O for Duke3D Dmo files.

Example:
    demo_file = dmo.Dmo.open('demo1.dmo')

References:
    "DMO format"
    - Paul Bourke
    - http://paulbourke.net/dataformats/dmo/
"""

import io
import struct


class BadDmoFile(Exception):
    pass


# The dmo header structure
header_format = '<i6B2h4i512si128s'


def compress(data):
    return b''


def decompress(lzwinbuf):
    strtot = 0
    currstr = 256
    numbits = 8
    oneupnumbits = 1 << 8
    i = 0
    dat = 0
    bitcnt = 4 << 3
    outbytecnt = 0
    longptr = None
    shortptr = None

    lzwbuf1 = {}
    lzwbuf2 = {}
    lzwbuf3 = {}

    lzwoutbuff = {}

    for i in range(256):
        lzwbuf2[i] = i
        lzwbuf3[i] = i

    while currstr < strtot:
        longptr = lzwinbuf[bitcnt >> 3]
        dat = longptr >> (bitcnt & 7) & (oneupnumbits - 1)
        bitcnt += numbits

        if dat & ((oneupnumbits >> 1) - 1) > ((currstr - 1) & ((oneupnumbits >> 1) - 1)):
            dat &= (oneupnumbits >> 1) - 1
            bitcnt -= 1

        lzwbuf3[currstr] = dat

        leng = 0
        while dat > 256:
            lzwbuf1[leng] = lzwbuf2[dat]
            leng += 1
            dat = lzwbuf3[dat]

        lzwoutbuff[outbytecnt] = dat
        outbytecnt += 1

        i = leng
        while i >= 0:
            lzwoutbuff[outbytecnt] = lzwbuf1[i]
            outbytecnt += 1
            i = i - 1

        lzwbuf2[currstr - 1] = dat
        lzwbuf2[currstr] = dat
        currstr += 1

        if currstr > oneupnumbits:
            numbits += 1
            oneupnumbits <<= 1

    return lzwoutbuff