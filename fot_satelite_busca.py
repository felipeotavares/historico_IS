# -*- coding: utf-8 -*-
"""
Created on Sun Aug  4 16:36:59 2024

@author: felip
"""

from cdasws import CdasWs
import matplotlib.pyplot as plt
cdas = CdasWs()

#%% Get Datasets

datasets = cdas.get_datasets(observatoryGroup='ACE',
                             instrumentType='Magnetic Fields (space)')
for index, dataset in enumerate(datasets):
    print(dataset['Id'], dataset['Label'])
    if index == 5:
        print('...')
        break
#%% Get Dataset Variables
variables = cdas.get_variables('AC_H1_MFI')
for variable in variables:
    print(variable['Name'], variable['LongDescription'])
    
#%%Get Dataset Variables
data = cdas.get_data('AC_H1_MFI', ['Magnitude', 'BGSEc'],
                     '2009-06-01T00:00:00Z', '2009-06-01T00:10:00Z')[1]
print(data)

#%% Display Metadata
print(data['Magnitude'].attrs)

#%% Plot Values
fig = data.plot(['Magnitude'])
fig.show()

#%%Display Original Data
dataset0 = 'AC_H0_SWE'
parameters = ['Np']
start = '1998-02-04T00:00:00Z'
stop = '1998-02-06T00:00:00Z'
status, data0 = cdas.get_data(dataset0, parameters, start, stop)
print(data0)
dataset1 = 'AC_H2_SWE'
status, data1 = cdas.get_data(dataset1, parameters, start, stop)
print(data1)

#%%Bin Data
binData = {
    'interval': 60.0,
    'interpolateMissingValues': True,
    'sigmaMultiplier': 4
}
status, data0 = cdas.get_data(dataset0, parameters, start, stop, binData=binData)
print(data0)
status, data1 = cdas.get_data(dataset1, parameters, start, stop, binData=binData)
print(data1)

#%%Compare Data
plt.plot(data0['Epoch_bin'], data0['Np'])
plt.plot(data1['Epoch_bin'], data1['Np'])
plt.xlabel(data0['Epoch'].attrs['LABLAXIS'])
plt.ylabel(data0['Np'].attrs['LABLAXIS'] + ' ' +
           data0['Np'].attrs['UNITS'])
plt.legend([dataset0, dataset1])
plt.show()