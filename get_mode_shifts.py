import pandas as pd
import numpy as np
import math
import itertools
from scipy.optimize import curve_fit


#constants
truck_speed = [45,45,45,45] #mph
rail_speed = 20 #mph
base = 0
compare = 1


data_df = pd.read_csv("pred2.csv").loc[:, 'dist_bin':'sum_wt']
rail_rate_df = pd.read_csv("input/RATES.csv").loc[:, 'SCTG':'RTM']
truck_rate_df = pd.ExcelFile("input/Rate Table per ton.xlsx").parse("Sheet1")



#select the columns from start to end
model1_df = pd.ExcelFile('./input/Modeparms(compare).xlsx').parse("Shpmt Freight Rate Models").loc[0:37, 'SCTG':'Group']
model2_df = pd.ExcelFile('./input/Modeparms(compare).xlsx').parse("22-Mkt Share Frt-Trans time").loc[0:3, 'SCTG':'Group']


#args = (50, '"19"', 100, 100)

#get_share(args)
def get_share(args):
    commodty, ann_tonnage, dist_bin, sum_wt = args[1], args[2], args[0], args[3]
    try:
        rl_rate_p_tm = float(rail_rate_df[(rail_rate_df['SCTG'].astype(str) == commodty) & (rail_rate_df['DGROUP'] == dist_bin)]['RTM'])
    except:
        rl_rate_p_tm1 = rail_rate_df[(rail_rate_df['SCTG'].astype(str) == commodty)][['DGROUP','RTM']]
        rl_rate_p_tm1 = rl_rate_p_tm1.append({'DGROUP':dist_bin, 'RTM':np.nan}, ignore_index=True)
        rl_rate_p_tm1 = rl_rate_p_tm1.sort_values(by='DGROUP').reset_index()[['DGROUP', 'RTM']]
        rl_rate_p_tm1 = rl_rate_p_tm1.interpolate(method='polynomial', axis=0, order = 3).ffill().bfill()
        rl_rate_p_tm = float(rl_rate_p_tm1[rl_rate_p_tm1['DGROUP']==dist_bin]['RTM'])
    truck_rate_pton_const = truck_rate_df[dist_bin].tolist()
    truck_rate_pton_const = [y for (x,y) in enumerate(truck_rate_pton_const) if x in [base,compare]]
    cost = [rl_rate_p_tm*ann_tonnage*dist_bin, truck_rate_pton_const[0]*ann_tonnage, truck_rate_pton_const[1]*ann_tonnage]
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
            b0 = float(model2_df[model2_df.SCTG == int(commodty.replace('"',""))]['b0'])
            bC = float(model2_df[model2_df.SCTG == int(commodty.replace('"',""))]['bC'])
            bT = float(model2_df[model2_df.SCTG == int(commodty.replace('"',""))]['bT'])
            Ur = bC * cost[0] + bT *  float(dist_bin) / rail_speed  #distance in miles divided by speed in mph
            _truck_speed_ = [y for (x,y) in enumerate(truck_speed) if x in [base,compare]]
            cost_transit_time = zip(cost[1:], [float(dist_bin)/x for x in _truck_speed_ ])
            Ut = [b0 + bC * x + bT *  y for x,y in cost_transit_time]  #distance in miles divided by speed in mph
        except:
            try: #there are commodities that would fit this model
                int("apple") #this would throw error
            except:
                print ("{0}, {1}, {2}".format(commodty, ann_tonnage, dist_bin))
                return -99,-99,-99, -99, -99, -99
    #print cost
    #print ("{0}.{1}".format(Ur, Ut))
    pt = [1.0/(1+np.exp(Ur-x)) for x in Ut]
    return Ur, Ut[0], Ut[1], pt[0], pt[1], rl_rate_p_tm

#drop any tonnages less than 75 tons/carload
data_df =data_df[data_df.sum_wt >= 75]

#data_df1[['Ur','Ut0','Ut1','pt0','pt1']] = []
#data_df1[['Ur','Ut0','Ut1','pt0','pt1']] = zip(*data_df.apply(get_share, axis = 1))
data_df['Ur'], data_df['Ut0'], data_df['Ut1'], data_df['pt0'], data_df['pt1'], data_df['rl_rate_ptm'] = zip(*data_df.apply(get_share, axis = 1))
data_df['tr_addi']= data_df['pt1']-data_df['pt0']
data_df['lost_ton'] = data_df['tr_addi'] *data_df['sum_wt']
data_df['lost_rev'] = data_df['rl_rate_ptm']*data_df['lost_ton'] *data_df['dist_bin']




data_df.to_csv("mode_split.csv")
