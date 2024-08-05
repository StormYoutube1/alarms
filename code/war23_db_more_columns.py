import pandas as pd
import numpy as np
import os

local = '/home/innereye/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    local = True
db = pd.read_csv('data/oct7database.csv')
idf = pd.read_csv('data/deaths_idf.csv')
map = pd.read_csv('data/oct_7_9.csv')
# btl = pd.read_excel('~/Documents/btl_yael_netzer.xlsx')
kidn = pd.read_csv('data/kidnapped.csv')
def get_idx(x, vec):
    i = np.where(vec == x)[0]
    if len(i) == 0:
        i = None
    elif len(i) == 1:
        i = i[0]
    else:
        raise Exception(f'too many {x} in vec')
    return i


def intize(m):
    if (type(m) == float or type(m) == np.float64) and ~np.isnan(m):
        m = int(m)
    return m

pid = db['pid'].values
# bid = btl['Column 1'].values
##
country = []
for ii in range(len(pid)):
    row = get_idx(pid[ii], idf['pid'].values)
    if row is not None:
        country.append('ישראל')
    # elif type(db['הנצחה'][ii]) == str and 'laad' in db['הנצחה'][ii]:
    #     id = int(db['הנצחה'][ii].split('ID=')[-1])
    #     row = get_idx(id, bid)
    #     if row:
    #         age.append(intize(btl['age'][row]))
    #     else:
    #         age.append(np.nan)
    elif pid[ii] in map['pid'].values:
        row = get_idx(pid[ii], map['pid'].values)
        if 'זרים' in map['citizenGroup'][row]:
            count = map['residence'][row].strip()
            country.append(count)
            if country[ii] != db['Residence'][ii].strip():
                raise Exception(f"{ii}: {count} != {db['Residence'][ii]}")
        else:
            country.append('ישראל')
    elif pid[ii] in kidn['pid'].values:
        row = get_idx(pid[ii], kidn['pid'].values)
        if kidn['status'][row] == 'זר':
            country.append(kidn['from'][row])
        else:
            country.append('ישראל')
    else:
        country.append(np.nan)

db['Country'] = country
db.to_csv('~/Documents/country.csv', index=False)
# fixed manually
##
db = pd.read_csv('data/oct7database.csv')
zar = np.where(db['Country'] != 'ישראל')[0]
for ii in zar:
    db.at[ii, 'Residence'] = db['מקום האירוע'][ii]
