# import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
# from datetime import datetime
import os
import Levenshtein
import re
# import re
local = '/home/innereye/alarms/'
# islocal = False

if os.path.isdir(local):
    os.chdir(local)
    local = True
csv = 'data/deaths_idf.csv'
idf = pd.read_csv(csv)
front = pd.read_csv('data/front.csv')
if all(front['name'].values == idf['name'].values[:len(front)]):
    pass
else:
    raise Exception('name mishmash')
##
to_fill = front['front'].isnull().values
#  from where to fill empty front cells
if not to_fill[-1]:
    to_fill = len(to_fill)
else:
    to_fill = np.where(~to_fill)[0][-1]+1

changed = False
if len(idf) >= to_fill:
    ynet = pd.read_csv('data/ynetlist.csv')
    yd = []
    for iy in range(len(ynet)):
        yd.append('|'.join([ynet['שם פרטי'][iy] + ' ' + ynet['שם משפחה'][iy],
                       str(ynet['גיל'][iy]), str(ynet['מקום מגורים'][iy])]))
    otef = '|'.join(['זיקים', 'נתיב העשרה', 'כפר עזה', 'נחל עוז', 'שדרות', 'בארי', 'כיסופים', 'מפלסים'])
    for ii in range(to_fill, len(idf)):
        st = idf['story'][ii]
        yy = ''
        ff = ''
        id = '|'.join([idf['name'][ii], str(idf['age'][ii]), str(idf['from'][ii])])
        distance = [Levenshtein.distance(id, x) for x in yd]
        if min(distance) < 3:
            yrow = np.argmin(distance)
            yy = ynet['מידע על המוות'][yrow]
        if (type(re.search(otef, yy)) == re.Match) or \
            (type(re.search(otef, st)) == re.Match):
            ff = 'עוטף עזה'
        elif (type(re.search(r'נפל בקרב.+רצוע', yy)) == re.Match) or \
             (type(re.search(r'נפל בקרב.+רצוע', st)) == re.Match):
            ff = 'עזה'
        elif 'לבנון' in yy or 'לבנון' in st:
            ff = 'לבנון'
        elif 'נרצח' in yy or 'נרצח' in st:
            ff = 'נרצח כאזרח'
        if len(yy) > 0 or len(ff) > 0:
            changed = True
        front.loc[ii] = [idf['name'][ii], st, yy, ff]
if changed:
    front.to_csv('data/front.csv', index=False)

# ##
# ynet = pd.read_csv('data/ynetlist.csv')
# # ynet = ynet[~ynet['דרגה'].isnull()]
# ynet = ynet.reset_index(drop=True)
# ynet['מקום מגורים'] = ynet['מקום מגורים'].str.replace('מושב ', '')
# idf['from'] = idf['from'].str.replace('מושב ', '')
# ##
# id = []
# for x in range(len(idf)):
#     id.append('|'.join([idf['name'][x], str(idf['age'][x]), str(idf['from'][x])]))
# id = np.array(id)
# idn = idf['name'].values
# ##
# idf['ynet'] = ''
# already = np.zeros(len(idf), bool)
# for iy in range(len(ynet)):
#     yd = '|'.join([ynet['שם פרטי'][iy] + ' ' + ynet['שם משפחה'][iy],
#                    str(ynet['גיל'][iy]), str(ynet['מקום מגורים'][iy])])
#
#     if yd in id:
#         idf_row = np.where(id == yd)[0][0]
#         # if idf_row == 17:
#         #     raise Exception('hudc')
#         if already[idf_row]:
#             raise Exception(f'already 0 {yd} {id[np.argmin(distance)]}')
#         idf.at[idf_row, 'ynet'] = ynet['מידע על המוות'][iy]
#         already[idf_row] = True
#     else:
#         missing = True
#         name = yd.split('|')[0]
#         for idf_row in range(len(idn)):
#             if id[idf_row].split('|')[1] == yd.split('|')[1]:  # age fit
#                 fit = 0
#                 for part in name.split(' '):
#                     if part in idn[idf_row]:
#                         fit += 1
#                 if fit > 1 and name != 'דניאל דני דרלינגטון':
#                     # if idf_row == 215:
#                     #     raise Exception('hudc')
#                     if already[idf_row]:
#                         raise Exception(f'already 1 {yd} {id[np.argmin(distance)]}')
#                     idf.at[idf_row, 'ynet'] = ynet['מידע על המוות'][iy]
#                     already[idf_row] = True
#                     missing = False
#                     break
#         # if (id[idf_row].split('|')[0].split(' ')[0] == yd.split('|')[0].split(' ')[0]) & \
#         #         id[idf_row].split('|')[1] == yd.split('|')[1]
#         if missing and name not in ['רותם קוץ']:
#             distance = [Levenshtein.distance(yd, x) for x in id]
#             idf_row = np.argmin(distance)
#             if min(distance) < 6 and idn[idf_row] not in ['אור מוזס', 'עמרי פרץ', 'גיא שמחי']:
#                 if idf_row == 266:
#                     raise Exception('hudc')
#                 if already[idf_row]:
#                     if name in ['מיכל אדמוני' ,'דין בר', 'שלו גל', 'אלירן מזרחי', 'יועד פאר',
#                                 'יונתן קוץ', 'אביב קוץ', 'אופק קמחי']:
#                         print('issue admoni')
#                     else:
#                         raise Exception(f'already 2 {yd} {id[np.argmin(distance)]}')
#                 else:
#                     idf.at[idf_row, 'ynet'] = ynet['מידע על המוות'][iy]
#                     already[idf_row] = True
#             else:
#                 print(f'{yd} {id[np.argmin(distance)]}')
# mis = ['יהונתן אהרן שטיינברג',
#        'רואי חיים גורי',
#        'אופיר ליבשטין',
#        'דוד (דודי) דגמי',
#        'חן יהלום']
# fnd = ['נהרג בכרם שלום',
#        'נהרג בקרב באופקים',
#        'ראש המועצה האזורית, נרצח בכפר עזה',
#        'נהרג בתאונת דרכים בחזרה הביתה מהמילואים',
#        'יצא להתרעננות של 24 שעות ונהרג בתאונה מפגיעת רכב במהלך אימון רכיבת אופניים סמוך לחולון']
# for ii, name in enumerate(mis):
#     row = np.where(idf['name'] == name)[0][0]
#     idf.at[row, 'ynet'] = fnd[ii]
# idf.to_csv('/home/innereye/Documents/idf+ynet.csv', index=False)
# ##
# idff = pd.read_csv('/home/innereye/Documents/idf+ynet.csv')
# idff['front'] = ''
# idx = np.where(idff['death_date'] == '2023-10-07')[0]
# for ii in idx:
#     idff.at[ii, 'front'] = 'עוטף עזה'
# idx = np.where(idff['ynet'].str.contains('תאונ'))[0]
# for ii in idx:
#     idff.at[ii, 'front'] = 'תאונה'
#
# idx = np.where(idff['story'].str.contains(r'נפל בקרב.+רצוע'))[0]
# for ii in idx:
#     idff.at[ii, 'front'] = 'עזה'
# idx = np.where(idff['ynet'].str.contains('נרצח'))[0]
# for ii in idx:
#     idff.at[ii, 'front'] = 'נרצח כאזרח'
# idx = np.where((idff['ynet'].str.contains('כוננות')) | (idff['ynet'].str.contains('רבש"')))[0]
# for ii in idx:
#     idff.at[ii, 'front'] = 'כיתת כוננות'
# idx = np.where(idff['ynet'].str.contains('לבנון'))[0]
# for ii in idx:
#     idff.at[ii, 'front'] = 'לבנון'
# idff.to_csv('tmp.csv')
# ##
# # if (id[idf_row].split('|')[0].split(' ')[0] == yd.split('|')[0].split(' ')[0]) & \
# #         id[idf_row].split('|')[1] == yd.split('|')[1]:
# #     idf.at[idf_row, 'ynet'] = ynet['מידע על המוות'][iy]
# # elif min(distance) < 8: