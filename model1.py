import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from geopy import distance
import math
import googlemaps

od_dist_time_dict = {}


# Requires API key
gmaps = googlemaps.Client(key='AIzaSyChD37gN3pUDQoLXB_sW3NcX6MOedEmoQ0')
# Requires cities name
o = (35.944574,-83.9898166)
d = (35.94,-83.98)

def get_dist_time(o,d):
    print (o,d)
    if (o,d) in od_dist_time_dict.keys():
        return od_dist_time_dict[(o,d)]
    result = gmaps.distance_matrix(o, d)
    print result
    time = result['rows'][0]['elements'][0]['duration']['text']
    dist = float((result['rows'][0]['elements'][0]['distance']['text'].split(" ")[0]).replace(",",""))/1.6
    od_dist_time_dict[(o, d)] = time,dist
    return (time,dist)






data = pd.read_csv("shortline_output.csv")
#data = pd.read_csv("sample_datat.csv")

type_bins = {'m':1, 'b':2}
distance_bins = {50:1, 200:2, 400:3, 600:4, 800:5, 1200:6}
#distance_bins = {200:1, 600:2}
use_rate_bins = {8000:1, 32000:2, 100000:3, 200000:4, 400000:5}
#use_rate_bins = {1000:1, 5000:2}

unique_distances = {1:1}

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


def get_od(dist):
    if dist in unique_distances.keys():
        return unique_distances[dist]
    else:
        maxi_mum = max(unique_distances.values())
        unique_distances[dist] = maxi_mum +1
        return maxi_mum + 1


# def get_coord_auto_man(aa):
#     try:
#         o = geolocator.geocode(aa)
#         return (o.latitude,o.longitude)
#     except:
#         print '"{0}": Not found'.format(aa)
#         return [0,1]


def get_e_distance(a,b):
    #print "{0}->{1}".format(a,b)
    if a in place_coordi_dict.keys():
        origin = place_coordi_dict[a]
    else:
        return 0
    if b in place_coordi_dict.keys():
        destination = place_coordi_dict[b]
    else:
        return 0
    dist = get_dist_time(origin,destination)[1]
    return dist

#calculating distance (temporary)
#data['dist1'] = data['dist1'].fillna(data['dist']*10)




#removing entries from dictionary
#place_coordi_dict = {x:y for x,y in place_coordi_dict.iteritems() if y != [0,1]}

#save
#pd.DataFrame.from_dict(od_dist_time_dict).transpose().to_csv("od_dist_time.csv")

#retrieve
dumm = pd.DataFrame.from_csv("od_dist_time.csv").reset_index()
dumm['new'] = "(" + dumm['index'] +"," + dumm['Unnamed: 1'] + ")"
dumm.drop(['index', 'Unnamed: 1'], axis = 1, inplace = True)
dumm  = dumm.set_index("new")
dumm1 = dumm.transpose().to_dict()
dumm2 = {eval(x):[y['0'], y['1']] for x,y in dumm1.iteritems()}
dumm2 = {x:(float(y['latlon'].split(',')[0]), float(y['latlon'].split(',')[1]))  for x,y in name_to_coord1.iteritems()}
od_dist_time_dict = dumm2



name_to_coord = pd.DataFrame.from_csv("name_to_coord.csv")
name_to_coord1 = name_to_coord.dropna().transpose().to_dict()
name_to_coord2 = {x:(float(y['latlon'].split(',')[0]), float(y['latlon'].split(',')[1]))  for x,y in name_to_coord1.iteritems()}
place_coordi_dict = name_to_coord2

#search on google maps

geolocator = Nominatim(user_agent = "rail_project_pdahal1")
data['d'] = data.apply(lambda x: get_e_distance(a = x['origin'], b = x['destination']), axis=1)
data['dist_bin'] = data['d'].map(get_dist_bin)
#just use this distance


data['type'] = data['cmdtymrt'].map(get_mb)


data.drop(['Unnamed: 0', 'False', 'cmdty', 'd1', 'dist', 'dist1', 'o1', 'rr', 'rr1', 'rr2' , 'origin', 'destination'], axis=1, inplace=True)


#for each unique value of od, give a distance called od
data['od'] = data['d'].map(get_od)





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
count_df.drop(['wt', 'od', 'd'] ,axis=1, inplace=True)
count_df = count_df.rename(columns = {'use_rate':'count'})

sum = count_df['count'].sum()

count_df['percent'] = ''
count_df['percent'] = count_df['count']/sum

#table2
avg_df = pd.pivot_table(data, values='wt', index=['dist_bin', 'type', 'use_rate_bin'], aggfunc=np.mean).reset_index()

#avg_df['combined'] = avg_df.type.astype(str) + "_"+ avg_df.use_rate_bin.astype(str) + "_" + avg_df.dist_bin.astype(str)


#predicted_df
no_of_shpmnt = 100000

predicted_1_df = avg_df.merge(count_df, on=['type', 'use_rate_bin', 'dist_bin'], how='left')
predicted_1_df['tons'] = predicted_1_df['wt'] * predicted_1_df['percent'] * no_of_shpmnt


predicted_1_df.to_csv("pred1.csv")


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
tonnage = 38260347803 #tons
predicted_2_df = sum_df.merge(avg_df, on=['type', 'use_rate_bin', 'dist_bin'], how='left')
predicted_2_df['shipments'] = (predicted_2_df['percent'] * tonnage / predicted_2_df['wt']).round(0)

predicted_2_df.to_csv("pred2.csv")