from adam_core.coordinates import KeplerianCoordinates, transform_coordinates, Origin
from astropy.time import Time
from adam_core.coordinates import Times
from adam_core.coordinates import Origin, OriginCodes
import rebound
import assist
from assist.impact import Impact
import unittest
import math
import numpy as np
import os
import ctypes

input_file = "100_impactors_ex.csv"

i = 0

with open(input_file, "r") as f:
    for line in f:

        if line.startswith("Obj"):
            with open("orbits_dates.csv", "w") as w:
                w.write(f"{line.strip()},impact_date\n")
            continue

        #individual elements broken out for clarity
        line_split = line.split(",")
        ObjID = line_split[0]
        print(ObjID)
        q_au = line_split[1]
        e = line_split[2]
        i_deg = line_split[3]
        argperi_deg = line_split[4]
        node_deg = line_split[5]
        tp_mjd = line_split[6]
        epoch_mjd = line_split[7]
        H_mag = line_split[8]
        a_au = line_split[9]
        M_deg = line_split[10]

        #convert to cartesian elements 
        time=Times.from_astropy(
                Time([epoch_mjd], scale="tdb", format="mjd")
            )
        print((Time([epoch_mjd], scale="tdb", format="mjd")).isot)
        keplerian_coordinates = KeplerianCoordinates.from_kwargs(
            a= [float(a_au)],
            e= [float(e)],
            i= [float(i_deg)],
            raan= [float(node_deg)],
            ap= [float(argperi_deg)],
            M= [float(M_deg)],
            time = time,
            origin = Origin.from_kwargs(code=["SUN"]),
            frame = "ecliptic",
        )

        cartesian_coordinates = keplerian_coordinates.to_cartesian()

        coords = transform_coordinates(
            cartesian_coordinates,
            origin_out=OriginCodes.SOLAR_SYSTEM_BARYCENTER,
            frame_out="equatorial",
        )

        values = coords.values[0]
        #print(values)

        time_jd = float(epoch_mjd) + 2400000.5

        vi_initial = rebound.Particle(x = values[0], # AU
                                            y =  values[1],
                                            z =  values[2],
                                            vx= values[3], # AU/day
                                            vy= values[4],
                                            vz= values[5])
        
        vi_initial_2 = rebound.Particle(x = values[0], # AU
                                            y =  values[1],
                                            z =  values[2],
                                            vx= values[3], # AU/day
                                            vy= values[4],
                                            vz= values[5])
        
        ephem = assist.Ephem("data/linux_p1550p2650.440", "data/sb441-n16.bsp")

        t_initial = time_jd - ephem.jd_ref # Julian Days relative to jd_ref

        sim = rebound.Simulation()
        sim.add(vi_initial)
        sim.add(vi_initial_2)
        sim.t = t_initial
        sim.ri_ias15.min_dt = 0.001
        extras = assist.Extras(sim, ephem)
        extras.gr_eih_sources = 11

        extras.particle_params = np.array([4.999999873689E-13, -2.901085508711E-14, 0.0])
        t_final = t_initial + 60
        #t_final = int(impact_dates[ObjID]) + 2400000.5 - ephem.jd_ref

        sim.integrate(t_final)

        def get_assist_impact():
            return extras.recorded_impacts

        get_assist_impact.restype = ctypes.POINTER(Impact)

        # Call the C function to get the struct pointer
        assist_impact_struct_ptr = get_assist_impact()

        # Dereference the pointer to get the actual Impact structure
        assist_impact_struct = assist_impact_struct_ptr.contents

        # Convert the arrays to Python lists
        n = assist_impact_struct.N  # Replace 10 with the actual length of your arrays
        print(n)
        impact_jd_list = [assist_impact_struct.impact_jd[i] for i in range(n)]
        impact_dist_list = [assist_impact_struct.impact_dist[i] for i in range(n)]

        print(impact_jd_list)
        print(impact_dist_list)