"""
Internal code: 0102b0a5fd
0 = Revision
1 = Vendor
02b0a5fd = ID code


External codes:

10H> 13D
10-digit hexadecimal (0102b0a5fd) decimal digits in 13
0004340098557

08H> 10D
8-digit hexadecimal (02b0a5fd) decimal digits in 10
0045131261


08H> 55D also called WEG32
2 by 4 hexadecimal digits (02B0, a5fd) in 2 x 5 decimal digits
00688.42493

06H> 08D
6 digit hexadecimal (b0a5fd) decimal digits in 8
11576829

2.4H> 3.5D (A)
2-digit hexadecimal (01) and 4-digit hexadecimal (a5fd)
decimal digits in 3 and 5 decimal digits
001.42493

2.4H> 3.5D (B)
2-digit hexadecimal (02) and 4-digit hexadecimal (a5fd)
decimal digits in 3 and 5 decimal digits
002.42493

2.4H> 3.5D (C), also called WEG24
2-digit hexadecimal (b0) and 4-digit hexadecimal (a5fd)
decimal digits in 3 and 5 decimal digits
176.42493

"""

WIEGAND_32 = 0x01
ACTICON = 0x02


def convert(format, uid):
    if format == WIEGAND_32:
        return convert_to_wiegand_32(uid)
    elif format == ACTICON:
        return convert_to_acticon(uid)


def convert_to_wiegand_32(uid):
    return int(bin(int(uid[1:], 16)), 2)


def convert_to_acticon(uid):
    return convert_to_wiegand_32(uid)
