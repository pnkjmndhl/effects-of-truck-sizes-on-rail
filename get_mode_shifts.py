import pandas as pd
import numpy as np
import math
import itertools
from scipy.optimize import curve_fit


#constants
data_df = pd.read_csv("pred2.csv").loc[:, 'dist_bin':'percent']
rail_rate_df = pd.read_csv("input/RATES.csv").loc[:, 'SCTG':'RTM']
truck_rate_df = pd.ExcelFile("input/Rate Table per ton.xlsx").parse("Sheet1")


def func(x,a,b):
    return (a*x*x+b*x+c)

#select the columns from start to end
model1_df = pd.ExcelFile('./input/Modeparms(compare).xlsx').parse("Shpmt Freight Rate Models").loc[0:35, 'SCTG':'Group']
model2_df = pd.ExcelFile('./input/Modeparms(compare).xlsx').parse("23-Mkt Share GC").loc[1:23, 'SCTG':'F']
#model3_df =


(commodty,ann_tonnage,dist_bin) = ('"13"', 173.825835, 50)

get_share(commodty, ann_tonnage, dist_bin)
def get_share(commodty, ann_tonnage, dist_bin):
    #print ("{0}, {1}, {2}".format(commodty, ann_tonnage, dist_bin))
    try:
        rl_rate_p_tm = float(rail_rate_df[(rail_rate_df['SCTG'].astype(str) == commodty) & (rail_rate_df['DGROUP'] == dist_bin)]['RTM'])
    except:
        rl_rate_p_tm1 = rail_rate_df[(rail_rate_df['SCTG'].astype(str) == commodty)][['DGROUP','RTM']]
        rl_rate_p_tm1 = rl_rate_p_tm1.append({'DGROUP':dist_bin, 'RTM':np.nan}, ignore_index=True)
        rl_rate_p_tm1 = rl_rate_p_tm1.sort_values(by='DGROUP').reset_index()[['DGROUP', 'RTM']]
        rl_rate_p_tm1 = rl_rate_p_tm1.interpolate(method='polynomial', axis=0, order = 3).ffill().bfill()
        rl_rate_p_tm = float(rl_rate_p_tm1[rl_rate_p_tm1['DGROUP']==dist_bin]['RTM'])
    rate_pton_const = truck_rate_df[dist_bin].loc[0:1].tolist() #just first and second row
    cost = [rl_rate_p_tm*ann_tonnage*dist_bin, rate_pton_const[0]*ann_tonnage, rate_pton_const[1]*ann_tonnage]
    #calculation
    try: #model1
        b0 = float(model1_df[model1_df.SCTG == int(commodty.replace('"',""))]['b0'])
        br = float(model1_df[model1_df.SCTG == int(commodty.replace('"',""))]['br'])
        gen_b0 = model1_df.loc[0:0,:]['b0'][0]
        gen_br = model1_df.loc[0:0,:]['br'][0]
        Ur = cost[0]*(gen_br + br)
        Ut = [(gen_b0 + b0) + x*(br+ gen_br) for x in cost[1:]]
    except:
        try: #model2
            b0 = float(model2_df[model2_df.SCTG == int(commodty.replace('"', ""))]['b0'])
            br = float(model2_df[model2_df.SCTG == int(commodty.replace('"', ""))]['bGC5'])
            gen_b0 = model2_df.loc[0:0, :]['b0'][0]
            gen_br = model2_df.loc[0:0, :]['br'][0]
            Ur = cost[0] * (gen_b0 + b0)
            Ut = [(gen_b0 + b0) + x * (br + gen_br) for x in cost[1:]]
        except:
            return [-99,-99]
    #print cost
    #print ("{0}.{1}".format(Ur, Ut))
    pt = [1.0/(1+np.exp(Ur-x)) for x in Ut]
    return pt[1]-pt[0]


data_df['new'] = data_df.apply(lambda x: get_share(x['commodty'], x['sum_wt'], x['dist_bin']), axis = 1)
data_df.to_csv("mode_split.csv")
