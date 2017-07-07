###############################################################################
# -*- coding: utf-8 -*-
# Order: A tool to characterize the local structure of liquid water 
#        by geometric order parameters
# 
# Authors: Pu Du
# 
# Released under the MIT MIT License
###############################################################################


"""Orientational Tetrahedral Order q
==============================================================
"""

from __future__ import print_function, division
import os
import six
from six.moves import range
import numpy as np

from . import util


class Orientational(object):
    """orientational tetrahedral order parameter"""

    def __init__(self, trajectory, center, bins=100):
        self.traj = trajectory
        self.center = center
        self.bins = bins
        base = os.path.basename(self.traj.filename)
        self.fprefix = os.path.splitext(base)[0]
        self.Q = np.zeros(bins+1)
    
    def four_neighbors(self, coords, L):
        """compute four nearest water oxygen neighbors"""
        dist = np.zeros([self.traj.n_atoms, self.traj.n_atoms], dtype=np.float)
        for i in range(self.traj.n_atoms - 1):
            for j in range(i + 1, self.traj.n_atoms):
                dx, dy, dz = coords[i] - coords[j]

                #periodic boundary conditions
                dx, dy, dz = util.pbc(dx, dy, dz, L)

                dist_ij = np.sqrt(dx * dx + dy * dy + dz * dz)
                dist[i][j] = dist_ij
                dist[j][i] = dist_ij
        
        my_vector = np.zeros([self.traj.n_atoms, 4, 3], dtype=float)

        for i in range(self.traj.n_atoms):
            my_list = dist[i]
            four_ns = [a[0] for a in sorted(enumerate(myList), key=lambda x:x[1])][1:5]
            j = 0
            for index in four_ns:
                dx, dy, dz = coords[index] - coords[i]

                #periodic boundary conditions
                dx, dy, dz = util.pbc(dx, dy, dz, L)

                my_vector[i][j] = [dx, dy, dz]
                j += 1
        return my_vector

    def orientational_param(self, freq = 1):
        """compute orientational order parameter"""
        for i in range(0, self.traj.n_frames, freq):
            foo = self.four_neighbors(self.traj.coords, self.traj.box_size)
            for j in range(self.traj.n_atoms):
                if self.traj.atom_names[i][j] == self.center:
                    q = 0.0
                    for k in range(3):
                        for l in range(k + 1, 4):
                            #cos_phi = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
                            cos_phi = util.cos_angle(foo[j][k], foo[j][l])
                            q += (cos_phi + 1 / 3) ** 2
                    q = 1 - 3 / 8 * q
                    if q > 0:
                        self.Q[int(round(q * self.bins))] += 1

    def out_put(self):
        """output raw data Q"""
        with open(self.fprefix + 'OTO.dat', 'w') as f:
            f.write("#OTO generated by Order: A Python Tool\n")
            f.write("Q  count\n")
            q = 0.00
            for c in self.Q:
                f.write('{} {}\n'.format(q, c))
                q += 1 / self.bins