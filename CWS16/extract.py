import csv
import pandas as pd
import numpy as np



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

wayser = file[0:6]
tdis = file[534:539]
uton = file[383:390]
ucar = file[26:30]
expn = file[350:353]
xcar = file[377:383]
urev = file[82:91]
zvar = file[50:51]
orr = file[157:160]
trr = file[213:216]
stcc = file[310:317]



mydict = {x[0:6]:[x[534:539],x[383:390],x[26:30],x[350:353],x[377:383],x[82:91],x[50:51],x[157:160],x[213:216], x[310:317]] for x in file}



df = pd.DataFrame.from_dict(mydict).transpose()
df.columns = [['TDIS', 'UTON', 'UCAR', 'EXPN', 'XCAR', 'UREV', 'ZVAR', 'ORR', 'TRR', 'STCC']]


df['TDIS'] = df.TDIS.astype('float')/10
df['RTM'] = df.UREV.astype('float')/(df.TDIS.astype('float')*df.UTON.astype('float'))

#df['ZNUM'] = df['ZVAR'].apply(lambda x: 1 if x=='Z' else 0)


df['DGROUP'] = df.apply(lambda x:get_dist_bin(x['TDIS']), axis = 1)


#conditions
df['SUM'] = df.apply(lambda x: f(x.ORR, x.TRR), axis=1)
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



