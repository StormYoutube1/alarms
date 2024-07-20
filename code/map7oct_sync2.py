import pandas as pd
import os
import numpy as np
import sys
import Levenshtein


local = '/home/innereye/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    local = True
    file = open('.txt')
    url = file.read().split('\n')[0]
    file.close()
map7 = pd.read_json(url)
# nameh = map7['hebrew_name'].values
namee = map7['name'].values  # [(map7['status'].values == 'Murdered') | (map7['status'].values == 'Killed on duty')]
map = pd.read_csv('data/oct_7_9.csv')
name = map['eng'].values
##
# missing = [x.strip() for x in namee if x.strip() not in name]
missing = []
for ii in range(len(name)):
    row = np.where(namee == name[ii])[0]
    if len(row) == 1:
        map.at[ii, 'oct7map_pid'] = map7['pid'][row[0]]
    else:
        map.at[ii, 'oct7map_pid'] = 0
        missing.append(ii)
map['oct7map_pid'] = map['oct7map_pid'].values.astype(int)
map.to_excel('/home/innereye/Documents/pid.xlsx', index=False)

##
map7 = pd.read_json(url)
map = pd.read_csv('data/oct_7_9.csv')
cref = pd.read_csv('data/crossref.csv')
locs = pd.DataFrame(cref['oct_7_9_fullName'])
for ii in range(len(locs)):
    pid = cref['oct7map_pid'][ii]
    if pid > 0:
        row = np.where(map7['pid'] == pid)[0][0]
        locs.at[ii, 'oct7map_name'] = map7['name'][row]
locs['oct_7_9_loc'] = map['location']
for ii in range(len(locs)):
    pid = cref['oct7map_pid'][ii]
    if pid > 0:
        row = np.where(map7['pid'] == pid)[0][0]
        locs.at[ii, 'oct7map_loc'] = map7['location'][row]
        locs.at[ii, 'oct7map_subloc'] = map7['sublocation'][row]
        locs.at[ii, 'oct7map_est'] = map7['Estimated location?'][row]
        locs.at[ii, 'oct7map_coo'] = map7['geotag'][row]

# subloc = np.unique(locs['oct7map_subloc'][locs['oct7map_coo'].isnull()].values.astype(str))
subloc = {'232 Blocked Road': [31.399963, 34.474210],
          'Alumim Bomb Shelter (West)': [31.450412, 34.516401],
          "Be'eri Bomb Shelter": [31.428803, 34.496924],
          'Gama Junction Bomb Shelter (North)': [31.381336, 34.447480],
          'Gama Junction Bomb Shelter (West)': [31.380127, 34.447162],
          "Hostage Situation in Be'eri": [],
          'Main Stage': [31.397771, 34.469951],
          'Nahal Grar Bridge': [31.400212, 34.474301],
          'Nova Ambulance': [31.397351, 34.469556],
          'Nova Bar': [31.398900, 34.470031],
          'Nova Entrance Bomb Shelter': [31.400190, 34.473742],
          "Re'im Bomb Shelter (East)": [31.389740, 34.459447],
          "Re'im Bomb Shelter (West)": [31.428803, 34.496924],
          'Yellow Containers': [31.398628, 34.470782]}

for ii in range(len(locs)):
    pid = cref['oct7map_pid'][ii]
    coo = str(locs['oct7map_coo'][ii])
    if pid > 0 and coo[:2] != '31':
        row = np.where(map7['pid'] == pid)[0][0]
        sl = map7['sublocation'][row]
        if str(sl) not in ['nan', 'None']:
            locs.at[ii, 'oct7map_coo'] = str(subloc[sl])[1: -1]


maploc = pd.read_csv('data/deaths_by_loc.csv')
locrow = np.where(~maploc['oct7map'].isnull())[0]
for lr in locrow:
    trow = np.where(locs['oct7map_loc'].values == maploc['oct7map'][lr])[0]
    for tr in trow:
        locs.at[tr, 'oct7map_coo'] = str(maploc['lat'][lr])+', '+str(maploc['long'][lr])


other = {'The pensioners bus in Sderot': '31.522808876615766, 34.59568825785523',
         'Sderot Police Station': '31.522808876615766, 34.59568825785523',
         'Erez': '31.55999246335105, 34.56505148304494',
         'Kerem Shalom': '31.228310751744882, 34.28445082924824',
         'COGAT Base': '31.55987823169991, 34.54622846569096'}

for othr in list(other.keys()):
    trow = np.where(locs['oct7map_loc'].values == othr)[0]
    for tr in trow:
        locs.at[tr, 'oct7map_coo'] = other[othr]

locs.to_csv('data/tmp_locs.csv', index=False)
##
from geopy.distance import geodesic
##
names = pd.read_csv('data/oct_7_9.csv')
replace = [['בכניסה לעלומים'], ['ביה"ח שיפא'], ['סמוך לצומת גמה', 'צומת גמה'], ['מיגונית בצומת גמה', 'צומת גמה'],
           ['צומת בארי'], ['מיגוניות בצומת רעים', 'צומת רעים'], ['חאן יונס'],
           ['רצועת עזה', 'רצועת עזה, לא פורסם מיקום מדוייק'], ['דיר אל בלח']]  #
for uu in replace:
    names.loc[names['location'].str.contains(uu[0]), 'location'] = uu[-1]  # -1 allows for pairs, search term + what to change into

for ii in range(len(locs)):
    trow = np.where(maploc['name'].values == names['location'][ii])[0][0]
    coo79 = [maploc['lat'][trow], maploc['long'][trow]]
    try:
        coo7 = np.array(locs['oct7map_coo'][ii].replace(' ', '').split(',')).astype(float)
        dif = geodesic(coo7, coo79).km
        locs.at[ii, 'dif'] = np.round(dif,1)
    except:
        locs.at[ii, 'dif'] = np.nan
locs.to_csv('data/tmp_locs.csv', index=False)

##
difs = locs.copy()
difs = difs[~difs['dif'].isnull()]
difs = difs.sort_values('dif', ascending=False, ignore_index=True)
difs = difs[difs['dif'] >= 1]
difs.to_csv('data/tmp_dif.csv', index=False)