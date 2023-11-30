from ctypes import (CFUNCTYPE, POINTER, Structure, byref, c_char, c_char_p,
                    c_double, c_int, c_long, c_uint, c_uint32, c_ulong,
                    c_void_p, cast)


class Impact(Structure):
    _fields_ = [
        ("N", c_int),
        ("hash", POINTER(c_uint32)),
        ("impact_jd", POINTER(c_double)),
        ("impact_dist", POINTER(c_double)),
        ("x", POINTER(c_double)),
        ("y", POINTER(c_double)),
        ("z", POINTER(c_double)),
        ("vx", POINTER(c_double)),
        ("vy", POINTER(c_double)),
        ("vz", POINTER(c_double)),
    ]
