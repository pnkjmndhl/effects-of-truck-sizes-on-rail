import pandas as pd
import numpy as np
import math
import itertools


#constants
model1_df = pd.read_csv("pred2.csv")

# truck_mileage = 200/1.1
# avg_shipm = 200
# ann_tonnage = 1000
# commodty = 'M'
# avg_value = 0.5  # /lb
# annual_int_rate = 0.05
# rl_circuity = 1.1


def get_share(commodty, ann_tonnage, truck_mileage, avg_shipm):
    rl_rate_p_tm = 0.0428
    loss_damage = [0.0005,0.0001,0.0001]
    rate_tm_const = [0.92,0.96]
    reliability_cost = [0,0,0]
    handling_cost = [0,0,0]
    speed = [5,35,35]  # mph
    handling_times = [8, 1, 1.1]  # hr
    sizes = [avg_shipm, 20, 23]
    #calculation
    trip_miles = [truck_mileage*1.1, truck_mileage, truck_mileage]
    avg_shipments = [float(ann_tonnage)/x for x in sizes] #size for each shipment for rail
    transit_time = [x / y for x, y in zip(trip_miles, speed)]
    #costs
    value = [avg_value*2000*x for x in sizes]
    total_time = [x + y for x, y in zip(transit_time, handling_times)]
    time_val_p_shp = [x*(pow(1+annual_int_rate/365,(float(y)/24))-1) for x,y in zip(value,total_time)]
    rate_p_tm = [rl_rate_p_tm] + [x/y for x,y in zip(rate_tm_const,sizes[1:])]
    shpmt_cost = [x*y*z for x,y,z in zip(rate_p_tm,sizes,trip_miles)]
    loss_damage_cost = [avg_value*x*y*2000 for x,y in zip(sizes,loss_damage)]
    total_cost_p_shp = [a+b+c+d+e for a,b,c,d,e in zip(shpmt_cost,loss_damage_cost,time_val_p_shp,reliability_cost,handling_cost)]
    total_cost = [x*y for x,y in zip(total_cost_p_shp,avg_shipments)]
    share = []
    for x in total_cost[1:]:
        share.append(float(1)/(1+ math.exp((total_cost[0] - x)/1000000)))
    new_tons = [x/share[0]*ann_tonnage for x in share[1:]]
    lost_revenue = [-1*(new_tons[0]-ann_tonnage)*rl_rate_p_tm*trip_miles[0] for x in new_tons]
    return (share,new_tons, lost_revenue)

model1_df['new'] = ""
model1_df['new'] = model1_df.apply(lambda x: get_share(x['commodty'], x['pred_tons'], x['dist_bin'], x['avg_wt']), axis=1)

#unpacking
