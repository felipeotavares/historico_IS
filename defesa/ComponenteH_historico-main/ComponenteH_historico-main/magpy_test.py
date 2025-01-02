# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 11:07:15 2024

@author: felip
"""

from magpy.stream import *

# print(PYMAG_SUPPORTED_FORMATS)

# data = read(example1)

data = read('https://imag-data-staging.bgs.ac.uk/GIN_V1/GINServices?request=GetData&observatoryIagaCode=WIC&dataStartDate=2021-03-10T00:00:00Z&dataEndDate=2021-03-11T23:59:59Z&Format=iaga2002&elements=&publicationState=adj-or-rep&samplesPerDay=minute')

A = data.fit

# help(DataStream().fit)

import magpy.mpplot as mp
mp.plot(data)