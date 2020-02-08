import pandas as pd
import numpy as np


#data = pd.read_csv("shortline_output.csv")
data = pd.read_csv("sample_datat.csv")

type_bins = {'m':1, 'b':2}
#distance_bins = {50:1, 200:2, 400:3, 600:4, 800:5, 1200:6}
distance_bins = {200:1, 600:2}
#use_rate_bins = {8000:1, 32000:2, 100000:3, 200000:4, 400000:5}
use_rate_bins = {1000:1, 5000:2}



#functions
def get_dist_bin(val):
    diff_list = [abs(x-val) for x in distance_bins.keys()]
    min_val = min(diff_list)
    min_val_index = diff_list.index(min_val)
    bin = distance_bins.keys()[min_val_index]
    return bin


def use_rate_bin(val):
    diff_list = [abs(x-val) for x in use_rate_bins.keys()]
    min_val = min(diff_list)
    min_val_index = diff_list.index(min_val)
    bin = use_rate_bins.keys()[min_val_index]
    return bin


def get_mb(val):
    if val in [1,2,3]:
        return 'm'
    else:
        return 'b'


#get bins
data['dist_bin'] = data['dist'].map(get_dist_bin)

#calculating use rate
use_rate_df = pd.pivot_table(data, values='wt', index=['type', 'od' ], aggfunc=np.sum).reset_index()
use_rate_df = use_rate_df.rename(columns = {'wt':'use_rate'})
use_rate_df['use_rate_bin'] = use_rate_df['use_rate'].map(use_rate_bin)

#data.wt = data.wtpcr * data.nos

#merging the use rate to the original data
data = data.merge(use_rate_df, on=['type', 'od'], how='left')

#data['combined'] = data.type.astype(str) + "_"+ data.use_rate_bin.astype(str) + "_" + data.dist_bin.astype(str)



#drop unnecessary (may be changed later)
# data.drop(["cmdty",'False', 'index', 'Unnamed: 0'],axis=1, inplace=True)
# data.drop(["destination",'d1', 'dist1', 'o1', 'origin', 'rr1', 'rr2','nos', 'wtpcr', 'dist' ,'rr' ],axis=1, inplace=True)

#dataforging
#randomly assign od values from 1 to 50 to a column named od
#data['od'] = np.random.randint(1, 50, data.shape[0])

data = data.dropna()
#data['type'] = data['cmdtymrt'].map(get_mb)


#SHIPMENT BASED MODEL
#table 1
count_df = data.groupby(['type', 'use_rate_bin', 'dist_bin']).count().reset_index() #use any column
count_df.drop(['wt', 'od', 'dist'] ,axis=1, inplace=True)
count_df = count_df.rename(columns = {'use_rate':'count'})

sum = count_df['count'].sum()

count_df['percent'] = ''
count_df['percent'] = count_df['count']/sum

#table2
avg_df = pd.pivot_table(data, values='wt', index=['dist_bin', 'type', 'use_rate_bin'], aggfunc=np.mean).reset_index()

#avg_df['combined'] = avg_df.type.astype(str) + "_"+ avg_df.use_rate_bin.astype(str) + "_" + avg_df.dist_bin.astype(str)


#predicted_df
no_of_shpmnt = 36

predicted_1_df = avg_df.merge(count_df, on=['type', 'use_rate_bin', 'dist_bin'], how='left')
predicted_1_df['tons'] = predicted_1_df['wt'] * predicted_1_df['percent'] * no_of_shpmnt


#table3
sum_df = pd.pivot_table(data, values='wt', index=['dist_bin', 'type', 'use_rate_bin'], aggfunc=np.sum).reset_index()
sum = sum_df['wt'].sum()
# sum_m = sum_df[sum_df.type == 'm']['wt'].sum()
# sum_b = sum_df[sum_df.type == 'b']['wt'].sum()
sum_df = sum_df.rename(columns = {'wt':'sum_wt'})

sum_df['percent'] = ''
# sum_df.loc[(sum_df.type == 'm'), 'percent' ] = sum_df['sum_wt']/sum_m
# sum_df.loc[(sum_df.type == 'b'), 'percent' ] = sum_df['sum_wt']/sum_b
sum_df['percent'] = sum_df['sum_wt']/sum

#predicted_df2
tonnage = 42000
predicted_2_df = sum_df.merge(avg_df, on=['type', 'use_rate_bin', 'dist_bin'], how='left')
predicted_2_df['shipments'] = predicted_2_df['percent'] * tonnage / predicted_2_df['wt']