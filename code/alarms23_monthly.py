# import re
from matplotlib import colors
import folium
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import plotly.express as px


local = '/home/innereye/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    islocal = True
prev = pd.read_csv('data/alarms.csv')
last_alarm = pd.to_datetime(prev['time'][len(prev)-1])
last_alarm = last_alarm.tz_localize('Israel')
# prev = prev[prev['threat'] == 0]
prev = prev.reset_index(drop=True)
date = np.array([d[:10] for d in prev['time']])
month = np.array([d[:7] for d in prev['time']])
monthu = np.unique(month)
monthu = monthu[monthu >= ['2023-10']]
# last7dates = np.unique(date)[-7:]
now = np.datetime64('now', 'ns')
nowisr = pd.to_datetime(now, utc=True, unit='s').astimezone(tz='Israel')
nowstr = str(nowisr)[:16].replace('T', ' ')
# current_date = datetime.now()
# date_list = []
# for _ in range(7):
#     date_list.append(current_date.strftime('%Y-%m-%d'))
#     current_date -= timedelta(days=1)

# Reverse the list to have the dates in descending order
# date_list.reverse()
# Prin
# nid = []
# n = []
# for day in range(7):
#     idx = date == date_list[day]
#     nid.append(len(np.unique(prev['id'][idx])))
#     n.append(np.sum(idx))
#
#
# fig = px.bar(x=date_list, y=n, log_y=True)
# # fig = px.bar(prev, y=n, x='date',log_y=True)
# html = fig.to_html()
# file = open('docs/alarms_last_7_days.html', 'w')
# a = file.write(html)
# file.close()
##
# Make map
title_html = f'''
             <h3 align="center" style="font-size:16px"><b>Alarms in Israel per month, data from <a href="https://www.oref.org.il" target="_blank">THE NATIONAL EMERGENCY PORTAL</a>
             via <a href="https://www.tzevaadom.co.il/" target="_blank">צבע אדום</a>. last checked: {nowstr}</b></h3>
             '''
# gnames = date_list
# co = [[1/1.5, 196/255/1.5, 1/1.5], [0.25, 0.25, 1.0], [0.25, 0.9, 0.8], [0.25, 1, 0.25], [0.75, 0.75, 0.25], [0.82, 0.5, 0.35],
#       [1.0, 0.25, 0.25], [0, 0, 0]]
# chex = []
# for c in co:
#     chex.append(colors.to_hex(c))
color = '#000000'
lgd_txt = '<span style="color: {col};">{txt}</span>'
grp = []
for ic, gn in enumerate(monthu):
    show = False
    if ic == 0:
        show = True
    grp.append(folium.FeatureGroup(name=lgd_txt.format(txt=gn, col=color), show=show))

coo = pd.read_csv('data/coord.csv')
center = [coo['lat'].mean(), coo['long'].mean()]
##
map = folium.Map(location=center, zoom_start=7.5, tiles='cartodbpositron')
# folium.TileLayer('cartodbpositron').add_to(map)
# folium.TileLayer('https://tile.openstreetmap.de/{z}/{x}/{y}.png',
#                  attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors').add_to(map)
# folium.TileLayer('openstreetmap').add_to(map)
# for tile in tiles:
#     folium.TileLayer(tile).add_to(map)
map.get_root().html.add_child(folium.Element(title_html))
# columns = ['month'] + np.loc['cities']
coo = coo.sort_values('lat', ignore_index=True, ascending=False)
cities = prev['cities'].values
keep = [x in cities[date > '2023-10-07'] for x in coo['loc']]
if coo['loc'][0] == 'אל מסק':
    keep[0] = False  # where dehel is el masq?
coo = coo[keep]
coo = coo.reset_index(drop=True)
monthly = coo.copy()
for igroup in range(len(monthu)):
    # idx = (yyyy == year)
    dt = monthu[igroup]
    # if igroup == 0:
    #     idx = (date >= '2023-10-07') & (month == dt)
    # else:
    idx = month == dt
    loc = np.asarray(prev['cities'][idx])
    # locu = np.unique(loc)
    # size = np.zeros(len(locu), int)
    for iloc in range(len(monthly)):
        # row_coo = coo['loc'] == locu[iloc]
        # if np.sum(row_coo) == 1:
        lc = monthly['loc'][iloc]
        sz = np.sum(loc == lc)
        monthly.at[iloc, dt] = sz
        if sz > 0:
            lat = float(monthly['lat'][iloc])
            long = float(monthly['long'][iloc])
            tip = lc+':  ' + str(sz)  # + str(mag[ii]) + depth  + '<br> '
            alpha = 0.5
            # if igroup == 0:
            #     alpha = 0.25
            folium.CircleMarker(location=[lat, long],
                                tooltip=tip,
                                radius=float(np.max([sz**0.5*2, 1])),
                                fill=True,
                                fill_color=color,
                                color=color,
                                opacity=0,
                                fill_opacity=alpha
                                ).add_to(grp[igroup])
monthly.to_csv('data/war23_alarms_monthly.csv', index=False)

for ig in range(len(monthu)):
    grp[ig].add_to(map)
folium.map.LayerControl('topleft', collapsed=False).add_to(map)
html_name = "docs/war_alarms_monthly.html"
map.save(html_name)
# with open(html_name, 'r') as fid:
#     html = fid.read()
# # osmde = 'https://tile.openstreetmap.de/{z}/{x}/{y}.png'  # 'openstreetmap.de'
# # idx = [m.start() for m in re.finditer(osmde, html)]
# # html = html[:idx[1]] + html[idx[1]:].replace(osmde, 'openstreetmap.de')
# with open(html_name, 'w') as fid:
#     fid.write(html)
print('done')
