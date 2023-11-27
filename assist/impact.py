from ctypes import Structure, c_double, POINTER, c_int, c_uint, c_long, c_ulong, c_void_p, c_char_p, CFUNCTYPE, byref, c_uint32, c_uint, cast, c_char

class Impact(Structure):

    _fields_ =  [("impact_jd", POINTER(c_double)),
                 ("impact_dist", POINTER(c_double)),
            ]

