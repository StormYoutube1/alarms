import requests
from matplotlib import colors
import folium
import pandas as pd
import numpy as np
import os
import plotly.express as px
import sys
import re


dt = pd.read_json('https://datadashboard.health.gov.il/api/war-casualties/lastUpdate')
dtstr = dt['lastUpdate'][dt['projectName'] == 'war_casualties'].values[0]
# dt['lastUpdate'] = pd.to_datetime(dt['lastUpdate'])
# print(dt['lastUpdate'][dt['projectName'] == 'war_casualties'].values[0])
last_update = pd.to_datetime(dtstr, utc=True).astimezone(tz='Israel')

local = '/home/innereye/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    islocal = True

prev = pd.read_csv('data/casualties_by_severity.csv')
if str(last_update)[:19] > prev['time'].values[-1]:
    r = requests.get(url='https://datadashboard.health.gov.il/api/war-casualties/totalCasualtiesByStatus')
    data = r.json()
    by_severity = {}
    total = 0
    for d in data:
        if d['type'] == 'נפגעים לפי חומרה בקליטה':
            by_severity[d['status']] = d['casualtiesCount']
        elif d['status'] == 'סה"כ נפגעים':
            total = d['casualtiesCount']
    # df = pd.DataFrame(columns=['נפטרים במערכת הבריאות', 'אנוש', 'קשה', 'בינוני', 'קל', 'חרדה ונפש', 'לא ידוע'])
    columns=['נפטרים במערכת הבריאות', 'אנוש', 'קשה', 'בינוני', 'קל', 'חרדה ונפש', 'לא ידוע']
    new_row = [str(last_update)[:19]]
    for col in columns:
        new_row.append(by_severity[col])
    new_row.append(total)
    df.loc[len(df)] = new_row
    df.to_csv('data/casualties_by_severity.csv', index=False)
else:
    print('no new casualties update')
