from ctypes import (CFUNCTYPE, POINTER, Structure, byref, c_char, c_char_p,
                    c_double, c_int, c_long, c_uint, c_uint32, c_ulong,
                    c_void_p, cast)


class Impact(Structure):
    _fields_ = [
        ("impact_jd", POINTER(c_double)),
        ("impact_dist", POINTER(c_double)),
        ("hash", POINTER(c_uint32)),
        ("N", c_int),
    ]
