import struct
from typing import Tuple
import numpy as np
import bitarray

from abramov_system.keygen import AbramovPublicKey


def enter_name(public_key: AbramovPublicKey) -> Tuple[np.poly1d, str]:
    name = str(input("Enter a variable name: "))
    name_as_int = encode(name)
    enc_name = public_key.encrypt(name_as_int)
    return enc_name, name


def enter_value(public_key: AbramovPublicKey) -> Tuple[np.poly1d, int]:
    value = int(input("Enter a value: "))
    enc_value = public_key.encrypt(value)
    return enc_value, value


def encode(string) -> int:
    bit_arr = bitarray.bitarray(string)
    int_value = struct.unpack("<L", bit_arr)[0]
    return int_value

    # bits_arr = []
    # for c in string:
    #     bits = bin(ord(c))[2:]
    #     bits = '00000000'[len(bits):] + bits
    #     bits_arr.extend([int(b) for b in bits])
    # return bits_arr


# def decode(bits_arr):
#     chars = []
#     for b in range(len(bits_arr) // 8):
#         byte = bits_arr[b * 8:(b + 1) * 8]
#         chars.append(chr(int(''.join([str(bit) for bit in byte]), 2)))
#     return ''.join(chars)
