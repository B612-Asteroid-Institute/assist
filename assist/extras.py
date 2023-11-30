import math
import warnings
from ctypes import (CFUNCTYPE, POINTER, Structure, byref, c_char, c_char_p,
                    c_double, c_int, c_long, c_uint, c_uint32, c_ulong,
                    c_void_p, cast)
from typing import List, NoReturn

import numpy as np
import numpy.typing as npt
import rebound

from . import clibassist
from .ephem import Ephem
from .impact import Impact

ASSIST_FORCES = {
    "SUN"                : 0x01,
    "PLANETS"            : 0x02,
    "ASTEROIDS"          : 0x04,
    "NON_GRAVITATIONAL"  : 0x08,
    "EARTH_HARMONICS"    : 0x10,
    "SUN_HARMONICS"      : 0x20,
    "GR_EIH"             : 0x40,
    "GR_SIMPLE"          : 0x80,
    "GR_POTENTIAL"       : 0x100,
}

class Extras(Structure):
    """
    Main object used for all ASSIST operations, tied to a particular REBOUND simulation.
    This is an abstraction of the C struct assist_extras.
    """
    def __init__(self, sim: rebound.Simulation, ephem: Ephem):
        sim._extras_ref = self  # add a reference to this instance in sim to make sure it's not garbage collected_
        clibassist.assist_init(byref(self), byref(sim), byref(ephem))
        # set up units and frame to allow direct access to JPL Horizons via REBOUND
        sim.update_units(("au","day","massist"))
        sim.default_plane = "frame"
        self.extras_should_free_ephem = 0

    def __del__(self) -> None:
        clibassist.assist_free_pointers(byref(self))

    def detach(self, sim: rebound.Simulation) -> None:
        sim._extras_ref = None # remove reference to assist so it can be garbage collected
        clibassist.assist_detach(byref(sim), byref(self))

    def integrate_or_interpolate(self, t: float) -> None:
        clibassist.assist_integrate_or_interpolate(byref(self), c_double(t))

    @property
    def forces(self) -> List[str]:
        l = []
        for k in ASSIST_FORCES:
            if self._forces & ASSIST_FORCES[k]:  # type: ignore
                l.append(k)
        return l
    @forces.setter
    def forces(self, value: List[str]) -> None:
        if not isinstance(value, list):
            raise AttributeError("Forces need to be a list.")
        for elem in value:
            if not isinstance(elem, str):
                raise AttributeError("Each force needs to be a string.")
            if elem.upper() not in ASSIST_FORCES:
                raise AttributeError("Force '"+elem+"' not recognized. Needs to be one of the following: "+", ".join(ASSIST_FORCES))
        v = 0
        for k in ASSIST_FORCES:
            if k in value:
                v = v | ASSIST_FORCES[k]
        self._forces = c_int(v)

    @property
    def particle_params(self) -> NoReturn:
        raise AttributeError("Cannot get particle_params. Only setting is supported.")

    @particle_params.setter
    def particle_params(self, value: npt.NDArray[np.float64]) -> None:
        self._particle_params_reference = value.copy() # keep copy of array to avoid it beeing freed
        value_p = self._particle_params_reference.ctypes.data_as(POINTER(c_double))
        self._particle_params = value_p

    def get_impacts(self):
        """
        Retrieves recorded impacts and returns them as a list of dictionaries.
        Assumes a negative or NaN value in impact_jd indicates no impact recorded for that slot.
        """
        N_total = self.recorded_impacts.contents.N
        impacts_list = []
        for i in range(N_total):
            impact_jd = self.recorded_impacts.contents.impact_jd[i]
            impact_dist = self.recorded_impacts.contents.impact_dist[i]
            hash_ = self.recorded_impacts.contents.hash[i]
            x = self.recorded_impacts.contents.x[i]
            y = self.recorded_impacts.contents.y[i]
            z = self.recorded_impacts.contents.z[i]
            vx = self.recorded_impacts.contents.vx[i]
            vy = self.recorded_impacts.contents.vy[i]
            vz = self.recorded_impacts.contents.vz[i]

            # Check if the values represent a recorded impact
            if impact_jd > 0 and not math.isnan(impact_jd):
                impact_data = {
                    'hash': hash_,
                    'time': impact_jd,
                    'distance': impact_dist,
                    'x': x,
                    'y': y,
                    'z': z,
                    'vx': vx,
                    'vy': vy,
                    'vz': vz,
                }
                impacts_list.append(impact_data)

        return impacts_list


    _fields_ =  [("_sim", POINTER(rebound.Simulation)),
                 ("ephem", POINTER(Ephem)),
                 ("_ephem_cache", c_void_p),
                 ("extras_should_free_ephem", c_int),
                 ("geocentric", c_int),
                 ("last_state", POINTER(rebound.Particle)),
                 ("current_state", POINTER(rebound.Particle)),
                 ("_particle_params", POINTER(c_double)),
                 ("recorded_impacts", POINTER(Impact)),
                 ("steps_done", c_int),
                 ("_forces", c_int),
                 ("gr_eih_sources", c_int),
        ]

