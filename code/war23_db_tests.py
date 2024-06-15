import pandas as pd
import os
import numpy as np
import unittest
import sys
sys.path.append('code')

local = '/home/innereye/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    islocal = True

# data = pd.read_csv('/home/innereye/Documents/oct7database - Data.csv')
data = pd.read_csv('data/oct7database.csv')
omi = pd.read_csv('/home/innereye/Documents/oct7database - omissions.csv')
kidn = pd.read_csv('data/kidnapped.csv')
idf = pd.read_csv('data/deaths_idf.csv')
##
''' TODO
check that middle names and nicknames are present for both languages
check that all parts of a name are present in the corresponding url
'''


def duplicates(pid, names):
    dup = pd.DataFrame(columns=['idx', 'pid', 'name'])
    for ii in range(len(names)):
        row = np.where(names == names[ii])[0]
        row = row[row != ii]
        if len(row) == 1:
            dup.loc[len(dup)] = [ii, pid[row[0]], names[ii]]
        elif len(row) > 1:
            raise Exception('more than 2 '+names[ii])
    return dup


##
class TestDuplicates(unittest.TestCase):
    def duplicate_pid(self):
        pid = data['pid'].values
        # dup_df = duplicates(pid, pid)
        dup_pid = duplicates(pid, pid)
        duplicates_length = len(dup_pid)
        if duplicates_length > 0:
            print(f'PID Duplicates!!!! {np.unique(dup_pid["pid"])}'.replace('[', '').replace(']', ''))
        self.assertEqual(duplicates_length, 0)

    def duplicate_heb(self):
        pid = data['pid'].values
        names = []
        for ii in range(len(data)):
            names.append(data['שם פרטי'][ii] + ' ' + data['שם משפחה'][ii])
        names = np.array(names)
        dup_heb = duplicates(pid, names)
        dup_names = np.unique(dup_heb['name'])
        okay_dup = np.sort(['אור מזרחי', 'דניאל כהן', 'עמית כהן', 'רותם לוי', 'לידור לוי'])
        duplicates_length = len(dup_names)
        bad_name = [x for x in dup_names if x not in okay_dup]
        if duplicates_length != len(okay_dup):
            print('Hebrew Name duplicates!!!!'+str(bad_name).replace('[', '').replace(']', ''))
            dup_heb.to_csv('/home/innereye/Documents/dup.csv', index=False)
            print(' See: Documents/dup.csv')
        self.assertEqual(duplicates_length, len(okay_dup))

    def duplicate_eng(self):
        pid = data['pid'].values
        names = []
        for ii in range(len(data)):
            names.append(data['first name'][ii] + ' ' + data['last name'][ii])
        names = np.array(names)
        dup_eng = duplicates(pid, names)
        dup_names = np.unique(dup_eng['name'])
        okay_dup = np.sort(['Or Mizrahi', 'Daniel Cohen', 'Amit Cohen', 'Ohad Cohen', 'Rotem Levi'])
        duplicates_length = len(dup_names)
        bad_name = [x for x in dup_names if x not in okay_dup]
        if duplicates_length != len(okay_dup):
            print('English Name duplicates!!!!'+str(bad_name).replace('[', '').replace(']', ''))
            dup_eng.to_csv('/home/innereye/Documents/dup_eng.csv', index=False)
            print(' See: Documents/dup_eng.csv')
        self.assertEqual(duplicates_length, len(okay_dup))

    def duplicate_url(self):
        dfurl = data[~data['הנצחה'].isnull()]
        pid_url = dfurl['pid'].values
        dup_url = duplicates(pid_url, dfurl['הנצחה'].values)
        duplicates_length = len(dup_url)
        if duplicates_length > 0:
            du = np.unique([x.split('/')[-1] for x in dup_url['name']])
            print(f'URL Duplicates!!!! {du}'.replace('[', '').replace(']', ''))
        self.assertEqual(duplicates_length, 0)

    def rank_name(self):
        pid_rank = [data['pid'][x] for x in range(len(data)) if data['first name'][x] in ['sergeant', 'sergent', 'captain', 'lieutenant', 'major', 'colonel', 'class']]
        if len(pid_rank) > 0:
            print(f'rank in first name!!!! {pid_rank}'.replace('[', '').replace(']', ''))
        self.assertEqual(len(pid_rank), 0)

class TestOmissions(unittest.TestCase):
    def not_dropped(self):
        pid = data['pid'].values
        nd = [x for x in omi['pid'] if x in pid]
        n_not_dropped = len(nd)
        if n_not_dropped > 0:
            print(f'Not omitted!!!! {nd}'.replace('[', '').replace(']', ''))
        self.assertEqual(n_not_dropped, 0)

    def dropped(self):
        pid = data['pid'].values
        pid_okay = omi['duplicate'][~omi['duplicate'].isnull()].values
        dpd = [x for x in pid_okay if x not in pid]
        n_dropped = len(dpd)
        if n_dropped > 0:
            print(f'Omitted a valid PID!!!! {dpd}'.replace('[', '').replace(']', ''))
        self.assertEqual(n_dropped, 0)

    def all_acounted(self):
            pid = data['pid'].values
            pid_all = np.unique(list(omi['pid']) + list(pid))
            try:
                json = pd.read_json('https://service-f5qeuerhaa-ey.a.run.app/api/individuals')
            except:
                raise Exception('no internet?')
            pid_json = json['pid'].values
            unaccounted = [x for x in pid_json if x not in pid_all]
            n_missing = len(unaccounted)
            if n_missing > 0:
                print(f'Unaccounted for PID!!!! {unaccounted}'.replace('[', '').replace(']', ''))
            self.assertEqual(n_missing, 0)


map79 = pd.read_csv('data/oct_7_9.csv')


class Test79(unittest.TestCase):
    def extras79(self):
        pid = data['pid'].values
        ext = [x for x in map79['pid'] if x not in pid]
        n_extra = len(ext)
        if n_extra > 0:
            print(f'OCT_7_9 PID Not in DB!!!! {ext}'.replace('[', '').replace(']', ''))
        self.assertEqual(n_extra, 0)

    def unique_pid79(self):
        pid79 = map79['pid'].values
        len_unique = len(pid79) - len(np.unique(pid79))
        if len_unique > 0:
            dup79 = np.unique([x for x in pid79 if np.sum(pid79 == x) > 1])
            print(f'OCT_7_9 PID Not Unique!!!! {dup79}'.replace('[', '').replace(']', ''))
        self.assertEqual(len_unique, 0)


haa = pd.read_csv('data/deaths_haaretz+.csv')
class TestHaa(unittest.TestCase):
    def extras_haa(self):
        pid = data['pid'].values
        ext = [x for x in haa['pid'] if x not in pid]
        ext = np.array(ext)
        ext = np.unique(ext[~np.isnan(ext)]).astype(int)
        n_extra = len(ext)
        if n_extra > 0:
            print(f'haaretz+ PID Not in DB!!!! {ext}'.replace('[', '').replace(']', ''))
        self.assertEqual(n_extra, 0)

    def extras_kidnapped(self):
        pid = data['pid'].values
        pid_kidn = kidn['pid'].values
        extras = [x for x in pid_kidn if x not in pid]
        n_extra = len(extras)
        if n_extra > 0:
            print(f'kidnapped PID Not in DB!!!! {extras}'.replace('[', '').replace(']', ''))
        self.assertEqual(n_extra, 0)
    def missing_haa(self):  # TODO: add kidnapped
        pid = data['pid'].values
        pid_kidn = kidn['pid'].values
        pid_haa = haa['pid'].values
        missing = [x for x in pid if x not in pid_haa]
        missing = np.array(missing)
        missing = np.unique(missing[~np.isnan(missing)]).astype(int)
        missing = [x for x in missing if x not in pid_kidn]
        missing = [x for x in missing if x not in range(2024, 2031)]  # Gazans
        n_extra = len(missing)
        if n_extra > 0:
            print(f'pid not in haaretz+!!!! {missing}'.replace('[', '').replace(']', ''))
        self.assertEqual(n_extra, 0)



    def unique_haa(self):
        pid_haa = haa['pid'].values
        pid_haa = pid_haa[~np.isnan(pid_haa)]
        len_unique = len(pid_haa) - len(np.unique(pid_haa))
        if len_unique > 0:
            dup_haa = np.unique([x for x in pid_haa if np.sum(pid_haa == x) > 1])
            print(f'haartz+ PID Not Unique!!!! {dup_haa}'.replace('[', '').replace(']', ''))
        self.assertEqual(len_unique, 0)


#
class TestIDF(unittest.TestCase):
    def unique_idf(self):
        pid_idf = idf['pid'].values
        pid_idf = pid_idf[~np.isnan(pid_idf)]
        len_unique = len(pid_idf) - len(np.unique(pid_idf))
        if len_unique > 0:
            dup_idf = np.unique([x for x in pid_idf if np.sum(pid_idf == x) > 1])
            print(f'idf PID Not Unique!!!! {dup_idf}'.replace('[', '').replace(']', ''))
        self.assertEqual(len_unique, 0)
    def extras_idf(self):
        pid = data['pid'].values
        pid_idf = idf['pid'].values
        pid_idf = pid_idf[~np.isnan(pid_idf)].astype(int)
        ext = [x for x in pid_idf if x not in pid]
        ext = np.array(ext)
        # ext = np.unique(ext[~np.isnan(ext)]).astype(int)
        n_extra = len(ext)
        if n_extra > 0:
            print(f'idf PID Not in DB!!!! {ext}'.replace('[', '').replace(']', ''))
        self.assertEqual(n_extra, 0)

    def name_idf(self):
        pid = data['pid'].values
        pid_idf = idf['pid'].values
        pid_idf = pid_idf[~np.isnan(pid_idf)].astype(int)
        mismatch = 0
        pid_mismatch = []
        for ii in range(len(pid_idf)):
            row = np.where(pid == pid_idf[ii])[0]
            if len(row) == 1:
                row = row[0]
                first = data['שם פרטי'][row]
                name = idf['name'][ii]
                if first not in name:
                    print(f'IDF: pid={idf["pid"][ii]}, {first} not in {name}')
                    mismatch += 1
                    pid_mismatch.append(idf["pid"][ii])
        if mismatch > 0:
            print(f"idf name doesn't match !!!! {pid_mismatch}".replace('[', '').replace(']', ''))
        self.assertEqual(mismatch, 0)




##
oct7db_results = unittest.TestResult()
oct7suite = unittest.TestSuite(tests=[TestDuplicates('duplicate_pid'),
                                      TestDuplicates('duplicate_heb'),
                                      TestDuplicates('duplicate_eng'),
                                      TestDuplicates('duplicate_url'),
                                      TestDuplicates('rank_name'),
                                      TestOmissions('not_dropped'),
                                      TestOmissions('dropped'),
                                      TestOmissions('all_acounted'),
                                      Test79('extras79'),
                                      Test79('unique_pid79'),
                                      TestHaa('extras_haa'),
                                      TestHaa('unique_haa'),
                                      TestHaa('missing_haa'),
                                      TestIDF('unique_idf'),
                                      TestIDF('extras_idf'),
                                      TestIDF('name_idf'),
                                      ]
                               )

oct7suite.run(oct7db_results)
print('XXXXXXXXXXXXXXXXXXXXXXXX')
print('N tests failed = '+str(len(oct7db_results.failures))+'/'+str(oct7db_results.testsRun))  #+\
      # ' including '+str(len(oct7db_results.expectedFailures))+' expected failures')
print('N tests with bugs = '+str(len(oct7db_results.errors))+'/'+str(oct7db_results.testsRun))
if len(oct7db_results.failures) > 0:
    print('failed:')
    for fl in oct7db_results.failures:
        for msg in fl:
            print(msg)
if len(oct7db_results.errors) > 0:
    print('Errors:')
    print('-------')
    for err in oct7db_results.errors:
        for msg in err:
            print(msg)
print('XXXXXXXXXXXXXXXXXXXXXXXX')

##
