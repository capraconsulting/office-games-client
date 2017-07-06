def reverse_hex_nibbles(hex_string):
    return ''.join([''.join(reversed(hex_string[i:(i + 2)])) for i in range(0, len(hex_string), 2)])


def reverse_decimal(decimal):
    return ''.join(reversed([decimal[i:(i + 2)] for i in range(0, len(decimal), 2)]))


def nuid_to_reversed_decimal(nuid):
    return str(int(reverse_decimal(nuid), 16))


def reversed_decimal_to_nuid(reversed_decimal):
    return reverse_decimal(hex(int(reversed_decimal))[2:].zfill(8)).upper()


def msb_to_lsb(msb):
    new_value = 0
    for part in range(0, 8):
        old_part = msb >> part * 8 & 0xFF
        new_part = 0
        for i in range(0, 8):
            if old_part & (2 ** i) & 0xFF > 0:
                new_part += (2 ** (7 - i))
        new_value += new_part << part * 8
    return new_value
