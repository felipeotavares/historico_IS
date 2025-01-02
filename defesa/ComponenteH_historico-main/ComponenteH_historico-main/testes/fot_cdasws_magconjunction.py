# -*- coding: utf-8 -*-
"""
Created on Sun Aug  4 17:16:52 2024

@author: felip
"""
from hdpws.hdpws import HdpWs
from hdpws import NAMESPACES as NS
from hdpws.resourcetype import ResourceType as rt
from hdpws.spase import AccessURL

from cdasws import CdasWs
from cdasws.datarepresentation import DataRepresentation as dr

from IPython.core.display import HTML


#%% Setup
import numpy as np
from sscws.sscws import SscWs
from sscws.conjunctions import BoxConjunctionArea, ConditionOperator,\
    GroundStationCondition, GroundStationConjunction,\
    Satellite, SatelliteCondition, TraceCoordinateSystem
from sscws.coordinates import CoordinateComponent, CoordinateSystem,\
    SurfaceGeographicCoordinates
from sscws.request import DataRequest, QueryRequest, SatelliteSpecification
from sscws.timeinterval import TimeInterval
from sscws.tracing import BFieldTraceDirection, TraceType
ssc = SscWs()

hdp = HdpWs()
cdas = CdasWs()



#%%Get ObservedRegions

result = hdp.get_observed_regions()
observed_regions = result['ObservedRegion']
print(f'{len(observed_regions)} HDP Observed Regions:')
for value in observed_regions[0:9]:
    print(f'    {value}')
print('    ...')

# %%Get ObservatoryIDs

result = hdp.get_observatory_ids()
observatory_ids = result['ObservatoryID']
print(f'{len(observatory_ids)} HDP ObservatoryIDs:')
for value in observatory_ids[0:9]:
    print(f'    {value}')
print('    ...')

# %%Get groundstationsIDs

ground_stations = ssc.get_ground_stations()
ground_station_ids = [ground_station['Id'] for ground_station in ground_stations['GroundStation']]
print(f'{len(ground_station_ids)} SSC GroundStationIDs:')
for value in ground_station_ids[0:9]:
    print(f'    {value}')
print('    ...')

# %%Get sats list

satellites = ssc.get_observatories()
ssc.get
satelite_ids = [satellite['Id'] for satellite in satellites['Observatory']]
print(f'{len(satelite_ids)} SSC Observatories:')
for value in satelite_ids[0:9]:
    print(f'    {value}')
print('    ...')

#%% Define Conjunction Query
# The following code defines a query to find magnetic field line conjuctions of at least two THEMIS satellites with one of four THEMIS ground stations during the time from 2008-01-05T10:00:00Z to 2008-01-05T11:59:59Z.
sats = [
    Satellite('themisa', BFieldTraceDirection.SAME_HEMISPHERE),
    Satellite('themisb', BFieldTraceDirection.SAME_HEMISPHERE),
    Satellite('themisc', BFieldTraceDirection.SAME_HEMISPHERE),
    Satellite('themisd', BFieldTraceDirection.SAME_HEMISPHERE),
    Satellite('themise', BFieldTraceDirection.SAME_HEMISPHERE)
]
satellite_condition = SatelliteCondition(sats, 2)

box_conjunction_area = BoxConjunctionArea(TraceCoordinateSystem.GEO,
                                          3.00, 10.00)

ground_stations = [
    GroundStationConjunction('FSMI', 'THM_Fort Smith',\
        SurfaceGeographicCoordinates(59.98, -111.84),\
        box_conjunction_area),
    GroundStationConjunction('WHIT', 'THM_White Horse',\
        SurfaceGeographicCoordinates(61.01, -135.22),\
        box_conjunction_area),
    GroundStationConjunction('FSIM', 'THM_Fort Simpson',\
        SurfaceGeographicCoordinates(61.80, -121.20),\
        box_conjunction_area),
    GroundStationConjunction('GAK', 'THM_HAARP/Gakona',\
        SurfaceGeographicCoordinates(62.40, -145.20),\
        box_conjunction_area)
]
ground_stationsA = [ground_stations[2]]

idx = 14 #
idx = 142 #FSIM
teste = ground_stations['GroundStation'][idx]
A = ground_stations['GroundStation'][idx]['Id']
B = ground_stations['GroundStation'][idx]['Name']
C = ground_stations['GroundStation'][idx]['Location']['Latitude']
D = ground_stations['GroundStation'][idx]['Location']['Longitude']    

ground_stationsB =  [GroundStationConjunction(A, B,\
    SurfaceGeographicCoordinates(C, D),\
    box_conjunction_area)]

ground_stations = ground_stationsA
ground_stations = ground_stationsB
    
ground_station_condition = \
    GroundStationCondition(ground_stations,
                            TraceCoordinateSystem.GEO,
                            TraceType.B_FIELD)
conditions = [
    satellite_condition,
    ground_station_condition
]
query_request = \
    QueryRequest('Magnetic conjunction of at least 2 THEMIS satellites with one of 4 THEMIS ground stations during 2008 doy=1-5.',
                 TimeInterval('2008-01-05T0:00:00Z',
                              '2008-10-05T11:59:59Z'),
                 ConditionOperator.ALL,
                 conditions)
#%% Run Conjunction Query

conjunctions = ssc.get_conjunctions(query_request)

# %%Display the results
SscWs.print_conjunction_result(conjunctions)

#%% Setup For Access To CDAWeb Data
# The following is code to find the corresponding data from cdaweb. Note that you need to have installed CDF, spacepy, and cdasws as mentioned in prerequisites for the following.
import re
from cdasws import CdasWs
from cdasws.datarepresentation import DataRepresentation
import matplotlib.pyplot as plt
cdas = CdasWs()
gs_id = {
    'THM_Fort Smith': 'FSMI',
    'THM_White Horse': 'WHIT',
    'THM_Fort Simpson': 'FSIM',
    'THM_HAARP/Gakona': 'GAK'
}

def get_cdaweb_ds(name: str) -> str:
    if name.startswith("THM"):
        return 'THG_L2_MAG_' + gs_id[name]
    else:
        return 'TH' + name[-1].upper() + '_L2_FGM'

def get_a_mag_var_name(ds: str, names) -> str:
    match = re.search('^THG_L2_MAG_(\w*)$', ds)
    if match:
        station = match.group(1)
        return 'thg_mag_' + station.lower()
    else:
        for name in names:
            if name.endswith('fgs_btotal'):
                return name
    return None

# %% Get Data During Conjunctions

conjunctions = result['Conjunction']
conjunction = result['Conjunction'][0]

result = 


for conjunction in conjunctions:
    time_interval = conjunction['TimeInterval']
    start = time_interval['Start']
    end = time_interval['End']
    sats = []
    for sat_des in conjunction['SatelliteDescription']:
        sats.append(sat_des['Satellite'])
    sat = conjunction['SatelliteDescription'][0]['Satellite']
    gs = conjunction['SatelliteDescription'][0]['Description'][0]['TraceDescription']['Target']['GroundStation']
    datasets = [get_cdaweb_ds(gs)]
    print(gs)

    print(datasets)
    for sat in sats:
        datasets.append(get_cdaweb_ds(sat))
    for ds in datasets:
        var_name = get_a_mag_var_name(ds, cdas.get_variable_names(ds))
        #print('dataset, var_name:', ds, var_name)
        status, data = cdas.get_data(ds, [var_name], start, end,
                                     dataRepresentation = DataRepresentation.XARRAY)
        var_data = data[var_name]
        epoch_var_name = var_data.attrs['DEPEND_0']
        if var_data.ndim == 2:
            var_data = np.linalg.norm(var_data, axis = 1)
            data_label = 'delta magnitude ' + var_name
        else:
            data_label = 'delta ' + var_name
        mean = var_data.mean(axis = 0)
        delta_data = var_data - mean
        plt.plot(data[epoch_var_name], delta_data, label = data_label)

    plt.xlabel('UTC: ' + start.date().isoformat())
    plt.ylabel('Delta Magnetic Field Magnitude (nT)')
    plt.legend()
    plt.show()
