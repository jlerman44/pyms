"""
Classes to model GC-MS data
"""

 #############################################################################
 #                                                                           #
 #    PyMS software for processing of metabolomic mass-spectrometry data     #
 #    Copyright (C) 2005-8 Vladimir Likic                                    #
 #                                                                           #
 #    This program is free software; you can redistribute it and/or modify   #
 #    it under the terms of the GNU General Public License version 2 as      #
 #    published by the Free Software Foundation.                             #
 #                                                                           #
 #    This program is distributed in the hope that it will be useful,        #
 #    but WITHOUT ANY WARRANTY; without even the implied warranty of         #
 #    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
 #    GNU General Public License for more details.                           #
 #                                                                           #
 #    You should have received a copy of the GNU General Public License      #
 #    along with this program; if not, write to the Free Software            #
 #    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.              #
 #                                                                           #
 #############################################################################

import numpy
import math
import copy

from pyms.Utils.Error import error
from pyms.Utils.Utils import is_str, is_int, is_array, is_list, is_number
from pyms.Utils.IO import open_for_writing, close_for_writing

class GCMS_data(object):

    """
    @summary: Generic object for GC-MS data
        Contains raw data as a list of scans and times

    @author: Qiao Wang
    @author: Andrew Isaac
    @author: Vladimir Likic
    """

    def __init__(self, time_list, scan_list):

        """
        @summary: Initialize the GC-MS data

        @param time_list: List of scan retention times
        @type time_list: ListType
        @param scan_list: List of Scan objects
        @type scan_list: ListType

        @author: Qiao Wang
        @author: Andrew Isaac
        @author: Vladimir Likic
        """

        if not is_list(time_list) or not is_number(time_list[0]):
            error("'time_list' must be a list of numbers")
        if not is_list(scan_list) or not isinstance(scan_list[0], Scan):
            error("'scan_list' must be a list of Scan objects")

        self.__time_list = time_list
        self.__min_rt = min(time_list)
        self.__max_rt = max(time_list)

        self.__scan_list = scan_list
        self.__set_min_max_mass()

        self.__calc_tic()

    def __set_min_max_mass(self):

        """
        @summary: Sets the min and max mass value

        @author: Qiao Wang
        @author: Andrew Isaac
        @author: Vladimir Likic
        """

        mini = self.__scan_list[0].get_min_mass()
        maxi = self.__scan_list[0].get_max_mass()
        for scan in self.__scan_list:
            tmp_mini = scan.get_min_mass()
            tmp_maxi = scan.get_max_mass()
            if tmp_mini < mini:
                mini = tmp_mini
            if tmp_maxi > maxi:
                maxi = tmp_maxi
        self.__min_mass = mini
        self.__max_mass = maxi

    def get_min_mass(self):

        """
        @summary: Get the min mass value over all scans

        @return: The minimum mass of all the data
        @rtype: FloatType

        @author: Qiao Wang
        @author: Andrew Isaac
        @author: Vladimir Likic
        """

        return self.__min_mass

    def get_max_mass(self):

        """
        @summary: Get the max mass value over all scans

        @return: The maximum mass of all the data
        @rtype: FloatType

        @author: Qiao Wang
        @author: Andrew Isaac
        @author: Vladimir Likic
        """

        return self.__max_mass

    def get_index_at_time(self, time):

        """
        @summary: Returns the nearest index corresponding to the given time

        @param time: Time in seconds
        @type time: FloatType

        @return: Nearest index corresponding to given time
        @rtype: IntType

        @author: Lewis Lee
        @author: Tim Erwin
        @author: Vladimir Likic
        """

        if not is_number(time):
            error("'time' must be a number")

        if time < self.__min_rt or time > self.__max_rt:
            error("time %.2f is out of bounds (min: %.2f, max: %.2f)" %
                  (time, self.__min_rt, self.__max_rt))

        time_list = self.__time_list
        time_diff_min = self.__max_rt
        ix_match = None

        for ix in range(len(time_list)):

            time_diff = math.fabs(time-time_list[ix])

            if time_diff < time_diff_min:
                ix_match = ix
                time_diff_min = time_diff

        return ix_match

    def get_time_list(self):

        """
        @summary: Returns the list of each scan retention time

        @return: A list of each scan retention time
        @rtype: ListType

        @author: Qiao Wang
        @author: Andrew Isaac
        @author: Vladimir Likic
        """

        return copy.deepcopy(self.__time_list)

    def get_scan_list(self):

        """
        @summary: Return a list of the scan objects

        @return: A list of scan objects
        @rtype: ListType

        @author: Qiao Wang
        @author: Andrew Isaac
        @author: Vladimir Likic
        """

        return copy.deepcopy(self.__scan_list)

    def get_tic(self):

        """
        @summary: Returns the total ion chromatogram

        @return: Total ion chromatogram
        @rtype: pyms.GCMS.IonChromatogram

        @author: Andrew Isaac
        """

        return self.__tic

    def __calc_tic(self):
        """
        @summary: Calculate the total ion chromatogram

        @return: Total ion chromatogram
        @rtype: pyms.GCMS.IonChromatogram

        @author: Qiao Wang
        @author: Andrew Isaac
        @author: Vladimir Likic
        """

        intensities = []
        for scan in self.__scan_list:
            intensities.append(sum(scan.get_intensity_list()))
        ia = numpy.array(intensities)
        rt = copy.deepcopy(self.__time_list)
        tic = IonChromatogram(ia, rt)

        self.__tic = tic


class Scan(object):

    """
    @summary: Generic object for a single Scan's raw data

    @author: Qiao Wang
    @author: Andrew Isaac
    @author: Vladimir Likic
    """

    def __init__(self, mass_list, intensity_list):

        """
        @summary: Initialize the Scan data

        @param mass_list: mass values
        @type mass_list: ListType

        @param intensity_list: intensity values
        @type intensity_list: ListType

        @author: Qiao Wang
        @author: Andrew Isaac
        @author: Vladimir Likic
        """

        if not is_list(mass_list) or not is_number(mass_list[0]):
            error("'mass_list' must be a list of numbers")
        if not is_list(intensity_list) or \
           not is_number(intensity_list[0]):
            error("'intensity_list' must be a list of numbers")

        self.__mass_list = mass_list
        self.__intensity_list = intensity_list
        self.__min_mass = min(mass_list)
        self.__max_mass = max(mass_list)

    def __len__(self):

        """
        @summary: Returns the length of the Scan object

        @return: Length of Scan
        @rtype: IntType

        @author: Andrew Isaac
        """

        return len(self.__mass_list)

    def get_mass_list(self):

        """
        @summary: Returns the masses for the current scan

        @return: the masses
        @rtype: ListType

        @author: Qiao Wang
        @author: Andrew Isaac
        @author: Vladimir Likic
        """

        return copy.deepcopy(self.__mass_list)

    def get_intensity_list(self):

        """
        @summary: Returns the intensities for the current scan

        @return: the intensities
        @rtype: ListType

        @author: Qiao Wang
        @author: Andrew Isaac
        @author: Vladimir Likic
        """

        return copy.deepcopy(self.__intensity_list)

    def get_min_mass(self):

        """
        @summary: Returns the minimum m/z value in the scan

        @return: Minimum m/z
        @rtype: Float

        @author: Andrew Isaac
        """

        return self.__min_mass

    def get_max_mass(self):

        """
        @summary: Returns the maximum m/z value in the scan

        @return: Maximum m/z
        @rtype: Float

        @author: Andrew Isaac
        """

        return self.__max_mass

class IntensityMatrix(object):

    """
    @summary: Intensity matrix of binned raw data

    @author: Andrew Isaac
    """

    def __init__(self, time_list, mass_list, intensity_matrix):

        """
        @summary: Initialize the IntensityMatrix data

        @param time_list: Retention time values
        @type time_list: ListType

        @param mass_list: Binned mass values
        @type mass_list: ListType

        @param intensity_list: Binned intensity values per scan
        @type intensity_list: ListType

        @author: Andrew Isaac
        """

        # sanity check
        if not is_list(time_list) or not is_number(time_list[0]):
            error("'time_list' must be a list of numbers")
        if not is_list(mass_list) or not is_number(mass_list[0]):
            error("'mass_list' must be a list of numbers")
        if not is_list(intensity_matrix) or \
           not is_list(intensity_matrix[0]) or \
           not is_number(intensity_matrix[0][0]):
            error("'intensity_matrix' must be a list, of a list, of numbers")
        if not len(time_list) == len(intensity_matrix):
            error("'time_list' is not the same length as 'intensity_matrix'")
        if not len(mass_list) == len(intensity_matrix[0]):
            error("'mass_list' is not the same size as 'intensity_matrix'"
                " width")

        self.__time_list = time_list
        self.__mass_list = mass_list
        self.__intensity_matrix = intensity_matrix

        self.__min_mass = min(mass_list)
        self.__max_mass = max(mass_list)

    def get_size(self):

        """
        @summary: Gets the size of intensity matrix

        @return: Number of rows and cols
        @rtype: IntType

        @author: Qiao Wang
        @author: Andrew Isaac
        @author: Vladimir Likic
        """

        row = len(self.__intensity_matrix)
        col = len(self.__intensity_matrix[0])

        return row, col

    def get_ic_at_index(self, index):

        """
        @summary: Returns the ion chromatogram at the specified index

        @param index: Index of an ion chromatogram in the intensity data matrix
        @type index: IntType

        @return: Ion chromatogram at given index
        @rtype: IonChromatogram

        @author: Qiao Wang
        @author: Andrew Isaac
        @author: Vladimir Likic
        """

        index = int(index)
        try:
            ia = []
            for i in range(len(self.__intensity_matrix)):
                ia.append(self.__intensity_matrix[i][index])

        except IndexError:
            error("index out of bounds.")

        ia = numpy.array(ia)
        mass = self.get_mass_at_index(index)
        rt = copy.deepcopy(self.__time_list)

        return IonChromatogram(ia, rt, mass)

    def get_ic_at_mass(self, mass = None):

        """
        @summary: Returns the ion chromatogram for the specified mass
            The nearest binned mass to mass is used

        If no mass value is given, the function returns the total
        ion chromatogram.

        @param mass: Mass value of an ion chromatogram
        @type mass: IntType

        @return: Ion chromatogram for given mass
        @rtype: IonChromatogram
        """

        if mass == None:
            return self.get_tic()

        if mass < self.__min_mass or mass > self.__max_mass:
            error("mass is out of range")

        index = self.get_index_of_mass(mass)
        return self.get_ic_at_index(index)

    def get_mass_list(self):

        """
        @summary: Returns a list of the bin masses

        @return: Binned mass list
        @rtype: ListType

        @author: Qiao Wang
        @author: Andrew Isaac
        @author: Vladimir Likic
        """

        return copy.deepcopy(self.__mass_list)

    def get_ms_at_index(self, index):

        """
        @summary: Returns a mass spectrum for a given scan index

        @param index: The index of the scan
        @type index: IntType

        @return: Mass spectrum
        @rtype: pyms.GCMS.MassSpectrum

        @author: Andrew Isaac
        """

        scan = self.get_scan_at_index(index)

        return MassSpectrum(self.__mass_list, scan)

    def get_scan_at_index(self, index):

        """
        @summary: Returns the spectral intensities for scan index

        @param index: The index of the scan
        @type index: IntType

        @return: Intensity values of scan spectra
        @rtype: ListType

        @author: Andrew Isaac
        """

        if index < 0 or index >= len(self.__intensity_matrix):
            error("index out of range")

        return copy.deepcopy(self.__intensity_matrix[index])

    def get_min_mass(self):

        """
        @summary: Returns the maximum binned mass

        @return: The maximum binned mass
        @rtype: FloatType

        @author: Andrew Isaac
        """

        return self.__min_mass

    def get_max_mass(self):

        """
        @summary: Returns the maximum binned mass

        @return: The maximum binned mass
        @rtype: FloatType

        @author: Andrew Isaac
        """

        return self.__max_mass

    def get_mass_at_index(self, index):

        """
        @summary: Returns binned mass at index

        @param index: Index of binned mass
        @type index: IntType

        @return: Binned mass
        @rtype: IntType

        @author: Andrew Isaac
        """

        if index < 0 or index >= len(self.__mass_list):
            error("index out of range")

        return self.__mass_list[index]

    def get_index_of_mass(self, mass):

        """
        @summary: Returns the index of mass in the list of masses
            The nearest binned mass to mass is used

        @param mass: Mass to lookup in list of masses
        @type mass: FloatType

        @return: Index of mass closest to given mass
        @rtype: IntType

        @author: Andrew Isaac
        """

        best = self.__max_mass
        index = 0
        for i in range(len(self.__mass_list)):
            tmp = abs(self.__mass_list[i] - mass)
            if tmp < best:
                best = tmp
                index = i
        return index

## TODO: return IM as list of lists?

class IonChromatogram(object):

    """
    @summary: Models ion chromatogram

    An ion chromatogram is a set of intensities as a function of retention
    time. This can can be either m/z channel intensities (for example, ion
    chromatograms at m/z=65), or cumulative intensities over all measured
    m/z. In the latter case the ion chromatogram is total ion chromatogram
    (TIC).

    The nature of an IonChromatogram object can be revealed by inspecting
    the value of the attribute '__mass'. This is se to the m/z value of the
    ion chromatogram, or to None for TIC.

    @author: Lewis Lee
    @author: Vladimir Likic
    """

    def __init__(self, ia, time_list, mass=None):

        """
        @param ia: Ion chromatogram intensity values
        @type ia: numpy.array
        @param time_list: A list of ion chromatogram retention times
        @type time_list: ListType
        @param mass: Mass of ion chromatogram (Null if TIC)
        @type mass: IntType

        @author: Lewis Lee
        @author: Vladimir Likic
        """

        if not isinstance(ia, numpy.ndarray):
            error("'ia' must be a numpy array")
        if not is_list(time_list) or not is_number(time_list[0]):
            error("'time_list' must be a list of numbers")
        if len(ia) != len(time_list):
            error("Intensity array and time list differ in length")

        self.__ia = ia
        self.__time_list = time_list
        self.__mass = mass
        self.__time_step = self.__calc_time_step(time_list)

    def __len__(self):

        """
        @summary: Returns the length of the IonChromatogram object

        @return: Length of ion chromatogram
        @rtype: IntType

        @author: Lewis Lee
        @author: Vladimir Likic
        """

        return self.__ia.size

    def get_intensity_at_index(self, ix):

        """
        @summary: Returns intensity at given index

        @param ix: An index
        @type ix: IntType

        @return: Intensity value
        @rtype: FloatType

        @author: Lewis Lee
        @author: Vladimir Likic
        """

        if not is_int(ix):
            error("index not an integer")

        if ix < 0 or ix > self.__ia.size - 1:
            error("index out of bounds")

        return self.__ia[ix]

    def get_intensity_array(self):

        """
        @summary: Returns the entire intensity array

        @return: Intensity array
        @rtype: numpy.ndarray

        @author: Lewis Lee
        @author: Vladimir Likic
        """

        return self.__ia

    def get_time_at_index(self, ix):

        """
        @summary: Returns time at given index

        @param ix: An index
        @type ix: IntType

        @return: Time value
        @rtype: FloatType

        @author: Lewis Lee
        @author: Vladimir Likic
        """

        if not is_int(ix):
            error("index not an integer")

        if ix < 0 or ix > len(self.__time_list) - 1:
            error("index out of bounds")

        return self.__time_list[ix]

    def get_time_list(self):

        """
        @summary: Returns the time list

        @return: Time list
        @rtype: ListType

        @author: Lewis Lee
        @author: Vladimir Likic
        """

        return self.__time_list

    def get_time_step(self):

        """
        @summary: Returns the time step

        @return: Time step
        @rtype: FloatType

        @author: Lewis Lee
        @author: Vladimir Likic
        """

        return self.__time_step

    def __calc_time_step(self, time_list):

        """
        @summary: Calculates the time step

        @param time_list: A list of retention times
        @type time_list: ListType

        @return: Time step value
        @rtype: FloatType

        @author: Lewis Lee
        @author: Vladimir Likic
        """

        td_list = []
        for ii in range(len(time_list)-1):
            td = time_list[ii+1]-time_list[ii]
            td_list.append(td)

        td_array = numpy.array(td_list)
        time_step = td_array.mean()

        return time_step

    def is_tic(self):

        """
        @summary: Returns True if the ion chromatogram is a total ion
            chromatogram (TIC), or False otherwise

        @return: A boolean value indicating if the ion chromatogram
            is a total ion chromatogram (True) or not (False)
        @rtype: BooleanType

        @author: Lewis Lee
        @author: Vladimir Likic
        """

        if self.__mass == None:
            return True
        else:
            return False

    def write(self, file_name, minutes=False):

        """
        @summary: Writes the ion chromatogram to the specified file

        @param file_name: File for writing the ion chromatogram
        @type file_name: StringType
        @param minutes: A boolean value indicating whether to write
            time in minutes
        @type minutes: BooleanType

        @return: none
        @rtype: NoneType

        @author: Lewis Lee
        @author: Vladimir Likic
        """

        if not is_str(file_name):
            error("'file_name' must be a string")

        fp = open_for_writing(file_name)

        time_list = copy.deepcopy(self.__time_list)

        if minutes:
            for ii in range(len(time_list)):
                time_list[ii] = time_list[ii]/60.0

        for ii in range(len(time_list)):
            fp.write("%8.4f %#.6e\n" % (time_list[ii], self.__ia[ii]))

        close_for_writing(fp)

class MassSpectrum(object):

    """
    @summary: Models a binned mass spectrum

    @author: Andrew Isaac
    @author: Qiao Wang
    @author: Vladimir Likic
    """

    def __init__(self, mass_list, intensity_list):

        """
        @summary: Initialise the MassSpectrum

        @para mass_list: List of binned masses
        @type mass_list: ListType
        @para intensity_list: List of binned intensities
        @type intensity_list: ListType

        @author: Andrew Isaac
        @author: Qiao Wang
        @author: Vladimir Likic
        """

        if not is_list(mass_list) or not is_number(mass_list[0]):
            error("'mass_list' must be a list of numbers")
        if not is_list(intensity_list) or \
           not is_number(intensity_list[0]):
            error("'intensity_list' must be a list of numbers")
        if not len(mass_list) == len(intensity_matrix):
            error("'mass_list' is not the same size as 'intensity_matrix'")

        #TODO: should these be public, or accessed through methods???
        self.mass_list = mass_list
        self.mass_spec = intensity_list

    def __len__(self):

        """
        @summary: Length of the MassSpectrum

        @return: Length of the MassSpectrum (Number of bins)
        @rtype: IntType

        @author: Andrew Isaac
        @author: Qiao Wang
        @author: Vladimir Likic
        """

        return len(self.mass_list)