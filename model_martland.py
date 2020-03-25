import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from geopy import distance
import math
import googlemaps

# od_dist_time_dict = {}


# Requires API key
gmaps = googlemaps.Client(key='AIzaSyChD37gN3pUDQoLXB_sW3NcX6MOedEmoQ0')


def get_distance_time(o, d):
    if (o == 0 or d == 0):
        return (np.nan, np.nan)
    if (o, d) in od_dist_time_dict.keys():
        return od_dist_time_dict[(o, d)]
    result = gmaps.distance_matrix(o, d)
    print result
    time = result['rows'][0]['elements'][0]['duration']['text']
    dist = float((result['rows'][0]['elements'][0]['distance']['text'].split(" ")[0]).replace(",", "")) / 1.6
    od_dist_time_dict[(o, d)] = time, dist
    return (time, dist)


data = pd.read_csv("input/shortline_output_all.csv")
data.drop("cmdty", axis = 1, inplace = True)
data.rename(columns = {"commo_new":"cmdty"}, inplace = True)

#filtering of data
#data = data[data['inout'] == 'Originating']
data.drop(['inout'], axis = 1, inplace = True)

# data = pd.read_csv("sample_datat.csv")

commodty_bins = [1, 2, 3, 4, 5, 6, 7]
distance_bins = {50: 1, 200: 2, 400: 3, 600: 4, 800: 5, 1200: 6}
# distance_bins = {200:1, 600:2}
use_rate_bins = {100:1, 1000: 2, 2000:3, 8000: 4, 25000: 5, 50000: 6, 100000: 7}
# use_rate_bins = {1000:1, 5000:2}

#to get the use rate
unique_distances = {1: 1}


# functions
def get_dist_bin(val):
    diff_list = [abs(x - val) for x in distance_bins.keys()]
    min_val = min(diff_list)
    min_val_index = diff_list.index(min_val)
    bin = distance_bins.keys()[min_val_index]
    return bin


def use_rate_bin(val):
    diff_list = [abs(x - val) for x in use_rate_bins.keys()]
    min_val = min(diff_list)
    min_val_index = diff_list.index(min_val)
    bin = use_rate_bins.keys()[min_val_index]
    return bin


def get_od(dist):
    if dist in unique_distances.keys():
        return unique_distances[dist]
    else:
        maxi_mum = max(unique_distances.values())
        unique_distances[dist] = maxi_mum + 1
        return maxi_mum + 1


def get_coordinate(a):
    # print "{0}->{1}".format(a,b)
    if a in place_coordi_dict.keys():
        return place_coordi_dict[a]
    else:
        return 0


unique_od_ids = {1: 1000}


def get_unique_od_ids(a, b):
    # print "{0}->{1}".format(a,b)
    if (a, b) in unique_od_ids.keys():
        return unique_od_ids[(a, b)]
    else:
        value = max(unique_od_ids.values()) + 1
        unique_od_ids[(a, b)] = value
        #unique_od_ids[(b, a)] = value #origin to destination is different to destination to origin use rate
        return value


# calculating distance (temporary)
# data['dist1'] = data['dist1'].fillna(data['dist']*10)

# removing entries from dictionary
# place_coordi_dict = {x:y for x,y in place_coordi_dict.iteritems() if y != [0,1]}


# retrieve
dumm = pd.DataFrame.from_csv("od_dist_time.csv").reset_index()
dumm['new'] = "(" + dumm['index'] + "," + dumm['Unnamed: 1'] + ")"
dumm.drop(['index', 'Unnamed: 1'], axis=1, inplace=True)
dumm = dumm.set_index("new")
dumm1 = dumm.transpose().to_dict()
dumm2 = {eval(x): [y['0'], y['1']] for x, y in dumm1.iteritems()}
# dumm2 = {x:(float(y['latlon'].split(',')[0]), float(y['latlon'].split(',')[1]))  for x,y in name_to_coord1.iteritems()}
od_dist_time_dict = dumm2

name_to_coord = pd.DataFrame.from_csv("name_to_coord.csv")
name_to_coord1 = name_to_coord.dropna().transpose().to_dict()
name_to_coord2 = {x: (float(y['latlon'].split(',')[0]), float(y['latlon'].split(',')[1])) for x, y in
                  name_to_coord1.iteritems()}
place_coordi_dict = name_to_coord2

# search on google maps

geolocator = Nominatim(user_agent="rail_project_pdahal1")
data['a_cord'] = data['origin'].map(get_coordinate)
data['b_cord'] = data['destination'].map(get_coordinate)
data['d'] = data.apply(lambda x: get_distance_time(x['a_cord'], x['b_cord'])[1], axis=1)
data['dist_bin'] = data['d'].map(get_dist_bin)

# for each unique value of origin and destination (reversed), give a distance called od
data['od'] = data.apply(lambda x: get_unique_od_ids(x['origin'], b=x['destination']), axis=1)

# save
pd.DataFrame.from_dict(od_dist_time_dict).transpose().to_csv("od_dist_time.csv")

data = data.rename(columns={"cmdty": "commodty"})


data.drop(
    ['Unnamed: 0', 'o2', 'False', 'd1', 'dist', 'dist1', 'o1', 'rr', 'rr1', 'rr2', 'origin', 'destination',
     'a_cord', 'b_cord', 'wtpcr', 'nos'], axis=1, inplace=True)


# calculating use rate
use_rate_df = pd.pivot_table(data, values='wt', index=['commodty', 'od'], aggfunc=np.sum).reset_index()
use_rate_df = use_rate_df.rename(columns={'wt': 'use_rate'})
use_rate_df['use_rate_bin'] = use_rate_df['use_rate'].map(use_rate_bin)

# merging the use rate to the original data
data = data.merge(use_rate_df, on=['commodty', 'od'], how='left')

data = data.dropna()

# SHIPMENT BASED MODEL
# table 1
#calculating the count/percentages of no. of shipments in each commodity, use rate bin, and distance bin
count_df = data.groupby(['commodty', 'use_rate_bin', 'dist_bin']).count().reset_index()  # use any column
count_df.drop(['wt', 'od', 'd'], axis=1, inplace=True)
count_df = count_df.rename(columns={'use_rate': 'count'})

sum = count_df['count'].sum()
count_df['percent'] = ''
count_df['percent'] = count_df['count'] / sum

# table2
#calculate the average value of tonnage for each commodity, use rate bin, and distance bin
avg_df = pd.pivot_table(data, values='wt', index=['commodty', 'use_rate_bin', 'dist_bin'], aggfunc=np.mean).reset_index()

# predicted_df1
shpmnt = 100000
predicted_1_df = avg_df.merge(count_df, on=['commodty', 'use_rate_bin', 'dist_bin'], how='left')
predicted_1_df['tons'] = predicted_1_df['wt'] * predicted_1_df['percent'] * shpmnt
predicted_1_df.to_csv("pred1.csv")

#TONNAGE BASED MODEL
# table3
sum_df = pd.pivot_table(data, values='wt', index=['dist_bin', 'commodty', 'use_rate_bin'], aggfunc=np.sum).reset_index()
sum = sum_df['wt'].sum()
sum_df = sum_df.rename(columns={'wt': 'sum_wt'})
sum_df['percent'] = ''
sum_df['percent'] = sum_df['sum_wt'] / sum

# predicted_df2
tons = 1553501000*0.21
predicted_2_df = sum_df.merge(avg_df, on=['commodty', 'use_rate_bin', 'dist_bin'], how='left')
predicted_2_df['shipments'] = (predicted_2_df['percent'] * tons / predicted_2_df['wt']).round(0)
predicted_2_df['pred_tons'] = predicted_2_df['percent'] * tons
predicted_2_df = predicted_2_df.rename(columns={'wt': 'avg_wt'})


predicted_2_df.to_csv("pred2.csv")
