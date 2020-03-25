import csv
import pandas as pd
import numpy as np

#Note: To convert rows from sas to python, (x-1,y)


distance_bins = [50,100,200,400,600,800,1000,1200]


def f(a,b):
    class1 = [103,105,400,555,712,777,802,978]
    if a in class1:
        if b in class1:
            return 1
    else:
        return 0




def get_dist_bin(val):
    diff_list = [abs(x - val) for x in distance_bins]
    min_val = min(diff_list)
    _index_ = diff_list.index(min_val)
    return distance_bins[_index_]


def get_commo(value):
    value = str(value)
    if value[0] == '"':
        value = value[1:-1]
    value4 = '"' + value[0:4] +'"'
    value5 = '"' + value[0:5] +'"'
    try: #search value4, if not found, use value5
        dumm =  stcg_dict[value4]
        if dumm == '""': #if dumm is empty
            raise ValueError('Bro, did not find')
        found_dict[value] = dumm
        return dumm
    except:
        try:
            dumm = stcg_dict[value5]
            found_dict[value] = dumm
            return dumm
        except:
            value = '"' + value +'"'
            #if not found in both use the 49 dictionary
            try:
                dumm = stcg_49_dict[value]
                found_dict[value] = dumm
                return dumm
            except:
                not_found_dict[value] = [value4, value5]


file = open("CWS16UM.txt").readlines()
#file[1]->line1


d= {}
for i in range(len(file)):
    d.setdefault('wayser', []).append(file[i][0:6])
    d.setdefault('tdis', []).append(file[i][534:539])
    d.setdefault('uton', []).append(file[i][383:390])
    d.setdefault('ucar', []).append(file[i][26:30])
    d.setdefault('expn', []).append(file[i][350:353])
    d.setdefault('xcar', []).append(file[i][377:383])
    d.setdefault('urev', []).append(file[i][82:91])
    d.setdefault('zvar', []).append(file[i][50:51])
    d.setdefault('orr', []).append(file[i][157:160])
    d.setdefault('trr', []).append(file[i][213:216])
    d.setdefault('stcc', []).append(file[i][310:317])
    d.setdefault('ofip', []).append(file[i][563:568])
    d.setdefault('tfip', []).append(file[i][568:573])




df = pd.DataFrame.from_dict(d)

#montgomery, NC->37123
#moore, NC->37125
df1 = df[(df.tfip == '37123') | (df.tfip == '37125')]



df['tdis'] = df.tdis.astype('float')/10
df['RTM'] = df.urev.astype('float')/(df.tdis.astype('float')*df.uton.astype('float'))

#df['ZNUM'] = df['ZVAR'].apply(lambda x: 1 if x=='Z' else 0)


df['DGROUP'] = df.apply(lambda x:get_dist_bin(x['tdis']), axis = 1)


#conditions
df['SUM'] = df.apply(lambda x: f(x.orr, x.trr), axis=1)
df = df[(df.RTM < 0.5) & (df.SUM==0)]



conv_df = pd.read_csv("../conversion.csv")
STCG_df1 = pd.ExcelFile("../SCTG.xlsx").parse("STCC 4-digit").append(pd.ExcelFile("../SCTG.xlsx").parse("STCC 5-digit")).reset_index()[['STCC', 'SCTG']]
STCG_49 = pd.ExcelFile("../49.xlsx").parse("Sheet1").reset_index()[['STCC', 'SCTG']]

stcg_dict = STCG_df1.transpose().to_dict()
stcg_dict = {y['STCC']:y['SCTG'] for x,y in stcg_dict.iteritems()}

stcg_49_dict = STCG_49.transpose().to_dict()
stcg_49_dict = {y['STCC']:y['SCTG'] for x,y in stcg_49_dict.iteritems()}

df = df.reset_index()

not_found_dict = {}
found_dict = {}
commo_new = 'SCTG'
df[commo_new] = ''

for i in df.index:
        try:
            df.at[i, commo_new] = get_commo(df["STCC"][i])
        except:
            print("Not found")
            not_found_dict[df.at[i, commo_new]] = 0

df['COUNT'] = 1
table = pd.pivot_table(df, values=['RTM', 'COUNT'] , index=['SCTG', 'DGROUP'], aggfunc={'RTM':np.mean, 'COUNT': np.sum}).reset_index()


pd.DataFrame.from_dict(not_found_dict).transpose().to_csv('not_found.csv')
table.to_csv('RATES.csv')



