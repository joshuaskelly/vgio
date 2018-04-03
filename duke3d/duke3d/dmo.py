"""This module provides file I/O for Duke3D Dmo files.

Example:
    demo_file = dmo.Dmo.open('demo1.dmo')

References:
    "DMO format"
    - Paul Bourke
    - http://paulbourke.net/dataformats/dmo/
"""

import io
import os
import struct


class BadDmoFile(Exception):
    pass


# The dmo header structure
header_format = '<i6B2h4i512si128s'
header_size = struct.calcsize(header_format)


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


def decompress(compressed):
    """Decompress a list of output ks to a string."""
    # Build the dictionary.
    dict_size = 256
    dictionary = {i: bytes([i]) for i in range(dict_size)}

    compressed = io.BytesIO(compressed)

    # use StringIO, otherwise this becomes O(N^2)
    # due to string concatenation in a loop
    result = io.BytesIO()
    w = compressed.read(1)
    ws = struct.unpack('<B', w)[0]
    result.write(w)
    for k in compressed:
        if k in dictionary:
            entry = dictionary[k]
        elif k == dict_size:
            entry = w + w[0]
        else:
            raise ValueError('Bad compressed k: %s' % k)
        result.write(entry)

        # Add w+entry[0] to the dictionary.
        dictionary[dict_size] = w + entry[0]
        dict_size += 1

        w = entry
    return result.getvalue()

print(os.path.exists('C:\\Users\\Joshua\\Desktop\\DEMO1.DMO'))
with open('C:\\Users\\Joshua\\Desktop\\DEMO1.DMO', 'rb') as file:
    header_data = file.read(header_size)
    header_struct = struct.unpack(header_format, header_data)
    aimmode = file.read(1)

    while file.peek(1) != b'':
        leng = struct.unpack('<h', file.read(2))[0]
        buff = file.read(leng)
        d = decompress(buff)

    print()
