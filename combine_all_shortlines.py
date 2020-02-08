import pandas as pd
import re
import numpy as np

import sys

reload(sys)
sys.setdefaultencoding('utf8')

# final table columns
no_of_cars = "nos"
wt_per_car = "wtpcr"
commodity = "cmdty"
online_dist = "dist"
all_dist = "dist1"
start_rr = "rr1"
current_rr = "rr"
forwarded_rr = "rr2"
origin = 'origin'
destination = 'destination'
transfer_1 = "o1"
transfer_2 = "d1"
total_wt = 'wt'
inout = 'inout'

# extract from excel files
ACWR = pd.ExcelFile("./CARRIER_DATA2/ACWR.xlsx").parse("Sheet1")
AGR_BPRR = pd.ExcelFile("./CARRIER_DATA2/AGR_BPRR.xlsx").parse("Sheet1")
#FMRC = pd.ExcelFile("./CARRIER_DATA2/FMRC.xlsx").parse("Sheet1")
GNBC = pd.ExcelFile("./CARRIER_DATA2/GNBC.xlsx").parse("Sheet1")
INRR = pd.ExcelFile("./CARRIER_DATA2/INRR.xlsx").parse("Sheet1")
KYLE = pd.ExcelFile("./CARRIER_DATA2/KYLE_RAW2.xlsx").parse("Sheet1")
SJVR = pd.ExcelFile("./CARRIER_DATA2/SJVR.xlsx").parse("Sheet1")
WSOR = pd.ExcelFile("./CARRIER_DATA2/WSOR.xlsx").parse("Sheet1")
YSVR = pd.ExcelFile("./CARRIER_DATA2/YSVR.xlsx").parse("Sheet1")

# preparing acwr data ??? Interline Off-Line O/D
acwr = ACWR[['Sum of Num Of Cars', 'Median Weight', 'In Out', 'Commodity', 'Median Mileage from Station to Interchange',
             'Chrg Patron Id', 'Chrg Rule 260 Cd', 'Onl Patron Station Name', 'Interline Off-Line O/D']]

acwr['Chrg Rule 260 Cd'] = acwr['Chrg Rule 260 Cd'].replace('ABRDN', "Aberdeen, NC")
acwr['Chrg Rule 260 Cd'] = acwr['Chrg Rule 260 Cd'].replace('NORWO', "Norwood, NC")
acwr['Chrg Rule 260 Cd'] = acwr['Chrg Rule 260 Cd'].replace('CHLTE', "Charlotte, NC")

acwr['Onl Patron Station Name'] = acwr['Onl Patron Station Name'] + ", NC"

for i in range(len(acwr)):
    if acwr['In Out'].iloc[i] == 'In':
        acwr.at[i, 'rr1'] = acwr['Chrg Patron Id'].iloc[i]
        acwr.at[i, 'o1'] = acwr['Chrg Rule 260 Cd'].iloc[i]
        acwr.at[i, 'origin'] = acwr['Interline Off-Line O/D'].iloc[i]
        acwr.at[i, 'dest'] = acwr['Onl Patron Station Name'].iloc[i]
    elif acwr['In Out'].iloc[i] == 'Out':
        acwr.at[i, 'rr2'] = acwr['Chrg Patron Id'].iloc[i]
        acwr.at[i, 'd1'] = acwr['Chrg Rule 260 Cd'].iloc[i]
        acwr.at[i, 'origin'] = acwr['Onl Patron Station Name'].iloc[i]
        acwr.at[i, 'dest'] = acwr['Interline Off-Line O/D'].iloc[i]
    else:
        acwr.at[i, 'origin'] = np.nan
        acwr.at[i, 'dest'] = np.nan
        acwr.at[i, 'rr1'] = np.nan
        acwr.at[i, 'o1'] = np.nan
        acwr.at[i, 'rr2'] = np.nan
        acwr.at[i, 'd1'] = np.nan

acwr['dest'] = acwr['dest'].replace('Outbound Destinations Unknown', np.nan)

acwr = acwr.drop(['Chrg Patron Id', 'Chrg Rule 260 Cd', 'Interline Off-Line O/D', 'Onl Patron Station Name'],
                 axis=1)
acwr['rr'] = 'acwr'
acwr = acwr.rename(columns={'Sum of Num Of Cars': no_of_cars, 'Median Weight': total_wt, 'Commodity': commodity,
                            'Median Mileage from Station to Interchange': online_dist, 'rr1': start_rr,
                            'rr': current_rr, 'rr2': forwarded_rr, 'In Out': inout,
                            'o1': transfer_1, 'd1': transfer_2, 'origin': origin, 'dest': destination})

# done


# preparing AGR_BPRR data
agr = AGR_BPRR
agr = agr[['2017Total Cars', 'Average Net Weight', 'STCC Description', 'Interchange Road From', 'City Trip Start',
           'State Trip Start', 'City Trip End', 'State Trip End', 'Traffic Type',
           'Interchange Road To', 'Average TMS Miles', 'WB Origin', 'WB Destination', 'Railroad Id']]
agr = agr.replace(',   ', np.nan)
agr = agr.replace('Missing', np.nan)
agr = agr.replace('N/A', np.nan)

agr['start'] = agr['City Trip Start'] + ", " + agr['State Trip Start']
agr['end'] = agr['City Trip End'] + ", " + agr['State Trip End']

# switch OD columns if bprr
for i in range(len(agr)):
    if agr['Railroad Id'].iloc[i] == 'BPRR':
        start = agr['start'].iloc[i]
        end = agr['end'].iloc[i]
        agr.at[i, 'start'] = agr['WB Origin'].iloc[i]
        agr.at[i, 'end'] = agr['WB Destination'].iloc[i]
        agr.at[i, 'WB Origin'] = start
        agr.at[i, 'WB Destination'] = end

agr = agr.drop(
    ['City Trip Start', 'City Trip End', 'State Trip Start', 'State Trip End'],
    axis=1)  # seasonality could be added later

agr = agr.rename(
    columns={'2017Total Cars': no_of_cars, 'Average Net Weight': total_wt, 'STCC Description': commodity,
             'Average TMS Miles': online_dist, 'Interchange Road From': start_rr, 'Railroad Id': current_rr,
             'Interchange Road To': forwarded_rr, 'Traffic Type': inout,
             'start': transfer_1, 'end': transfer_2, 'WB Origin': origin, 'WB Destination': destination})

agr[total_wt] = agr[total_wt]/2000

# agr.to_csv("agr.csv")

# done

# preparing FMRC data
# FMRC incorporated through GNBC
# fmrc = FMRC
# fmrc['On-Line O/D'] = fmrc['On-Line O/D'] + ", OK"
# fmrc['Interchange Location'] = fmrc['Interchange Location'] + ", OK"
#
# for i in range(len(fmrc)):
#     if fmrc['Inbound or Outbound or Bridge'].iloc[i] == 'Inbound':
#         fmrc.at[i, 'rr1'] = fmrc['Interchange Railroad'].iloc[i]
#         fmrc.at[i, 'o1'] = fmrc['Interchange Location'].iloc[i]
#         fmrc.at[i, 'origin'] = fmrc['Off-Line O/D'].iloc[i]
#         fmrc.at[i, 'destination'] = fmrc['On-Line O/D'].iloc[i]
#     elif fmrc['Inbound or Outbound or Bridge'].iloc[i] == 'Outbound':
#         fmrc.at[i, 'rr2'] = fmrc['Interchange Railroad'].iloc[i]
#         fmrc.at[i, 'd1'] = fmrc['Interchange Location'].iloc[i]
#         fmrc.at[i, 'origin'] = fmrc['On-Line O/D'].iloc[i]
#         fmrc.at[i, 'destination'] = fmrc['Off-Line O/D'].iloc[i]
#     else:
#         fmrc.at[i, 'rr2'] = np.nan
#         fmrc.at[i, 'd1'] = np.nan
#         fmrc.at[i, 'origin'] = np.nan
#         fmrc.at[i, 'destination'] = np.nan
#         fmrc.at[i, 'rr1'] = np.nan
#         fmrc.at[i, 'o1'] = np.nan
#
# fmrc = fmrc.drop(
#     ['Inbound or Outbound or Bridge', 'Off-Line O/D', 'On-Line O/D', 'Interchange Location', 'Interchange Railroad',
#      "Local O/D", "Seasonality"], axis=1)  # seasonality could be added later
# fmrc['rr'] = 'fmrc'
# fmrc = fmrc.rename(
#     columns={'2017 Carloads': no_of_cars, 'Typical Net (Lading) Weight per Car': wt_per_car, 'Commodity': commodity,
#              'Online Shipment Distance': online_dist, 'rr1': start_rr, 'rr': current_rr, 'rr2': forwarded_rr,
#              'o1': transfer_1, 'd1': transfer_2, 'origin': origin, 'dest': destination})

# fmrc.to_csv("fmrc.csv")
# done

# preparing gnbc data
gnbc = GNBC
gnbc.replace({r'[^\x00-\x7F]+': ''}, regex=True, inplace=True)  # removing non-ascii characters

gnbc['online_od'] = gnbc['On-Line O/D County'] + ', ' + gnbc['On-Line O/D State']
gnbc['offline_od'] = gnbc['Off-Line O/D County'] + ', ' + gnbc['Off-Line O/D State']
for i in range(len(gnbc)):
    if gnbc['Inbound or Outbound or Bridge'].iloc[i] == 'Inbound':
        gnbc.at[i, 'rr1'] = gnbc['Interchange Railroad'].iloc[i]
        gnbc.at[i, 'o1'] = gnbc['Interchange Location'].iloc[i] + ", OK"
        gnbc.at[i, 'origin'] = gnbc['offline_od'].iloc[i]
        gnbc.at[i, 'destination'] = gnbc['online_od'].iloc[i]
    elif gnbc['Inbound or Outbound or Bridge'].iloc[i] == 'Outbound':
        gnbc.at[i, 'rr2'] = gnbc['Interchange Railroad'].iloc[i]
        gnbc.at[i, 'd1'] = gnbc['Interchange Location'].iloc[i] + ", OK"
        gnbc.at[i, 'origin'] = gnbc['online_od'].iloc[i]
        gnbc.at[i, 'destination'] = gnbc['offline_od'].iloc[i]
    else:  # local and bridge donot have enough information
        gnbc.at[i, 'rr2'] = np.nan
        gnbc.at[i, 'd1'] = np.nan
        gnbc.at[i, 'origin'] = np.nan
        gnbc.at[i, 'destination'] = np.nan
        gnbc.at[i, 'rr1'] = np.nan
        gnbc.at[i, 'o1'] = np.nan

gnbc = gnbc.drop(['online_od', 'offline_od', 'On-Line O/D County', 'On-Line O/D State',
                  'Off-Line O/D County', 'Off-Line O/D State', 'Interchange Location', 'Interchange Railroad',
                  "Local O/D", "Seasonality", 'On-Line O/D', 'Off-Line O/D', 'Unnamed: 15'],
                 axis=1)  # seasonality could be added later
gnbc['rr'] = 'gnbc'
gnbc = gnbc.rename(
    columns={'2017 Carloads': no_of_cars, 'Typical Net (Lading) Weight per Car': wt_per_car, 'Commodity': commodity,
             'Online Shipment Distance': online_dist, 'rr1': start_rr, 'rr': current_rr, 'rr2': forwarded_rr, 'Inbound or Outbound or Bridge':inout,
             'o1': transfer_1, 'd1': transfer_2, 'origin': origin, 'dest': destination})

gnbc[wt_per_car] = gnbc[wt_per_car]/2000
# gnbc.to_csv("gnbc.csv")
# done

# preparing INRR data
inrr = INRR[['2017 Carloads', 'Inbound or Outbound or Bridge', 'Typical Net (Lading) Weight per Car', 'Commodity',
             'Online Shipment Distance', 'Interchange Railroad', 'Interchange Location', 'On-Line O/D', 'Off-Line O/D']]
for i in range(len(inrr)):
    if inrr['Inbound or Outbound or Bridge'].iloc[i] == 'In':
        inrr.at[i, 'origin'] = inrr['Off-Line O/D'].iloc[i]
        inrr.at[i, 'dest'] = inrr['On-Line O/D'].iloc[i]
        inrr.at[i, 'rr1'] = inrr['Interchange Railroad'].iloc[i]
        inrr.at[i, 'o1'] = inrr['Interchange Location'].iloc[i]
    elif inrr['Inbound or Outbound or Bridge'].iloc[i] == 'Out':
        inrr.at[i, 'origin'] = inrr['On-Line O/D'].iloc[i]
        inrr.at[i, 'dest'] = inrr['Off-Line O/D'].iloc[i]
        inrr.at[i, 'rr2'] = inrr['Interchange Railroad'].iloc[i]
        inrr.at[i, 'd1'] = inrr['Interchange Location'].iloc[i]
    elif inrr['Inbound or Outbound or Bridge'].iloc[i] == 'Bridge':
        inrr.at[i, 'origin'] = inrr['On-Line O/D'].iloc[i]
        inrr.at[i, 'dest'] = inrr['Off-Line O/D'].iloc[i]
        inrr.at[i, 'rr1'] = inrr['Interchange Railroad'].iloc[i].split('-')[0]
        inrr.at[i, 'o1'] = inrr['Interchange Location'].iloc[i].split('-')[0]
        inrr.at[i, 'rr2'] = inrr['Interchange Railroad'].iloc[i].split('-')[1]
        inrr.at[i, 'd1'] = inrr['Interchange Location'].iloc[i].split('-')[1]
    elif inrr['Inbound or Outbound or Bridge'].iloc[i] == 'Local':
        inrr.at[i, 'origin'] = inrr['On-Line O/D'].iloc[i]
        inrr.at[i, 'dest'] = inrr['Off-Line O/D'].iloc[i]
    else:
        inrr.at[i, 'origin'] = np.nan
        inrr.at[i, 'dest'] = np.nan
        inrr.at[i, 'rr1'] = np.nan
        inrr.at[i, 'o1'] = np.nan
        inrr.at[i, 'rr2'] = np.nan
        inrr.at[i, 'd1'] = np.nan

inrr = inrr.drop(
    ['On-Line O/D', 'Off-Line O/D', 'Interchange Location', 'Interchange Railroad'],
    axis=1)
inrr['rr'] = 'inrr'
inrr = inrr.rename(
    columns={'2017 Carloads': no_of_cars, 'Typical Net (Lading) Weight per Car': wt_per_car, 'Commodity': commodity,
             'Online Shipment Distance': online_dist, 'rr1': start_rr, 'rr': current_rr, 'rr2': forwarded_rr, 'Inbound or Outbound or Bridge':inout,
             'o1': transfer_1, 'd1': transfer_2, 'origin': origin, 'dest': destination})

inrr[wt_per_car] = inrr[wt_per_car]/2000

# done

# preparing KYLE
kyle = KYLE
kyle = kyle[
    ['From Station/Road', 'To Station/Road', 'STCC', 'AVERAGE WEIGHT', 'Origin State',
     'Origin Station', 'Destination Station', 'Destination State', 'ROUTE ONLINE MILES', 'TYPE OF TRAFFIC']]
kyle['o1'] = kyle['Origin Station'].str.strip() + ', ' + kyle['Origin State']
kyle['d1'] = kyle['Destination Station'].str.strip() + ', ' + kyle['Destination State']

kyle = kyle.drop(['Origin Station', 'Origin State', 'Destination Station', 'Destination State'], axis=1)

kyle = kyle.rename(columns={'AVERAGE WEIGHT': total_wt, 'STCC': commodity, 'TYPE OF TRAFFIC': inout,
                            'ROUTE ONLINE MILES': online_dist, 'From Station/Road': start_rr,
                            'To Station/Road': forwarded_rr, 'o1': origin, 'd1': destination})
kyle = kyle.replace('Missing', np.nan)
kyle[total_wt] = kyle[total_wt]/2000
kyle['rr'] = 'kyle'

# done


#SJVR
# preparing KYLE
sjvr = SJVR
sjvr = sjvr[
    ['TYPE OF TRAFFIC','Commodity Name', 'Average weight', 'Origin Station', 'Origin State', 'Interchange Road',
     'Interchange Station', 'Dest Station', 'Dest State', 'Car Count', 'ROUTE ONLINE MILES',
     'TOTAL ONLINE MILES']]
sjvr['oo'] = sjvr['Origin Station'].str.rstrip() + ', ' + sjvr['Origin State']
sjvr['dd'] = sjvr['Dest Station'].str.rstrip() + ', ' + sjvr['Dest State']

sjvr['rr1'] = ''
sjvr['rr2'] = ''
sjvr['o1'] = ''
sjvr['o2'] = ''

for i in range(len(sjvr)):
    if sjvr['TYPE OF TRAFFIC'].iloc[i] == 'ORIGINATING':
        sjvr.at[i, 'rr2'] = sjvr['Interchange Road'].iloc[i]
        sjvr.at[i, 'd1'] = sjvr['Interchange Station'].iloc[i]
    elif sjvr['TYPE OF TRAFFIC'].iloc[i] == 'TERMINATING':
        sjvr.at[i, 'rr1'] = sjvr['Interchange Road'].iloc[i]
        sjvr.at[i, 'o1'] = sjvr['Interchange Station'].iloc[i]
    else:
        sjvr.at[i, 'rr1'] = np.nan
        sjvr.at[i, 'rr2'] = np.nan
        sjvr.at[i, 'o1'] = np.nan
        sjvr.at[i, 'd1'] = np.nan

sjvr = sjvr.drop(['Origin Station', 'Origin State', 'Dest Station', 'Dest State', 'Interchange Road', 'Interchange Station'], axis=1)

sjvr = sjvr.rename(columns={'Car Count': no_of_cars, 'Average weight': total_wt, 'Commodity Name': commodity,
                            'ROUTE ONLINE MILES': online_dist, 'Interchange Road From': start_rr, 'rr': current_rr, 'TYPE OF TRAFFIC':inout,
                            'Interchange Road To': forwarded_rr, 'oo': origin, 'dd': destination, 'TOTAL ONLINE MILES': all_dist})
sjvr['rr'] = 'sjvr'
sjvr[total_wt] = sjvr[total_wt]/2000



# preparing WSOR
# problems: where are the location of transfers gonna be?
# need to work on "Road & Junctions", the final or first taken
wsor = WSOR
# the bridge data has 0 tons so removed


wsor = wsor[wsor['IB/OB'] != 'BRIDGE']
# wsor = wsor.dropna() #removing "Total" calculated in the excel file, lets not be that aggressive
wsor = wsor.drop(['Seasonality'], axis=1)
wsor['Commodity'] = wsor['Commodity'].str.split('-',1).str[0]
for i in range(len(wsor)):
    if wsor['IB/OB'].iloc[i] == 'In':
        wsor.at[i, 'rr1'] = wsor['Road & Junctions'].iloc[i].split(' ')[0]
        wsor.at[i, 'o1'] = np.nan
    elif wsor['IB/OB'].iloc[i] == 'Out':
        try:
            wsor.at[i, 'rr2'] = wsor['Road & Junctions'].iloc[i].split(' ')[1]
        except:
            wsor.at[i, 'rr2'] = np.nan
        wsor.at[i, 'd1'] = np.nan

wsor = wsor.drop(['D-Rd', 'O-Rd', 'Road & Junctions'], axis=1)
wsor = wsor.rename(columns={'Sum of Total Cars': no_of_cars, 'Average of Tons': total_wt, 'Commodity': commodity,
                            'Average of Miles2': all_dist, 'rr1': start_rr, 'rr': current_rr, 'IB/OB':inout,
                            'Destination	D-Rd': forwarded_rr, 'o1': transfer_1, 'd1': transfer_2, 'Origin': origin,
                            'Destination': destination})

# data with total removed
wsor[commodity] = wsor[commodity].fillna('N/A')
wsor = wsor[~wsor[commodity].str.contains("Total")]
wsor[commodity == 'N/A'] = np.nan
wsor[destination] = wsor[destination].replace(',   ', np.nan)
wsor['rr'] = 'wsor'


# wsor.to_csv("wsor.csv")

# done


def get_rr1_rr2(listofrr):
    # list of rr has the string of RRS separated by , (ranges from one railroad to 5)
    # the remaining would only have spaces
    rrs = listofrr.split(",")
    rrs = [x for x in rrs if not re.match(r'[    ]', x)]
    try:
        index_of_rr = rrs.index('YSVR')
    except:
        print("YSVR not in the list")  # checked that origin is Dore, ND, rr2 always equals BNSF
        index_of_rr = -99
    if index_of_rr == 0:
        rr2 = rrs[1]
        rr1 = np.nan
    elif index_of_rr == len(rrs) - 1:
        rr1 = rrs[0]
        rr2 = np.nan
    elif index_of_rr == -99:
        rr1 = np.nan
        rr2 = rrs[0]
    else:
        rr1 = rrs[0]
        rr2 = rrs[index_of_rr + 1]
    return [rr1, rr2]


# preparing YSVR
# total weight given, weight per car not given
ysvr = YSVR[['STCC', 'ORIGIN', 'DEST', 'ROUTE ROAD 01', 'ROUTE ROAD 02', 'ROUTE ROAD 03', 'ROUTE ROAD 04',
             "ROUTE ROAD 05", "NET WEIGHT", "MILES", ]]
ysvr['rrlist'] = [
    row['ROUTE ROAD 01'] + "," + row['ROUTE ROAD 02'] + "," + row['ROUTE ROAD 03'] + "," + row['ROUTE ROAD 04'] + "," +
    row['ROUTE ROAD 05'] for index, row in ysvr.iterrows()]
ysvr['rr1'] = ''
ysvr['rr2'] = ''
for i in range(len(ysvr)):
    ysvr.at[i, 'rr1'], ysvr.at[i, 'rr2'] = get_rr1_rr2(ysvr['rrlist'].iloc[i])

ysvr = ysvr.drop(["rrlist", 'ROUTE ROAD 01', 'ROUTE ROAD 02', 'ROUTE ROAD 03', 'ROUTE ROAD 04', "ROUTE ROAD 05"],
                 axis=1)

def get_inout(val):
    if val == 'DORE , ND':
        return 'Outbound'
    else:
        return 'Inbound'


ysvr['inout'] = ysvr['ORIGIN'].map(get_inout)


ysvr = ysvr.rename(columns={'NET WEIGHT': total_wt, 'STCC': commodity,
                            'MILES': all_dist, 'rr1': start_rr, 'rr': current_rr, 'inout':inout,
                            'Destination	D-Rd': forwarded_rr, 'o1': transfer_1, 'd1': transfer_2, 'ORIGIN': origin,
                            'DEST': destination})

ysvr[total_wt] = ysvr[total_wt]/2000
ysvr['rr'] = 'ysvr'


# ysvr.to_csv("ysvr.csv")




# adding all to one
#all = wsor.append(acwr).append(agr).append(fmrc).append(gnbc).append(inrr).append(kyle).append(sjvr).append(wsor).append(ysvr)
all = wsor.append(acwr).append(agr).append(gnbc).append(inrr).append(kyle).append(sjvr).append(wsor).append(ysvr)

# all maths
all = all[all[commodity].notnull()] #commodity cant be null
#all = all[all[no_of_cars].notnull()]
#all = all[all[wt_per_car].notnull()]
#all = all[all[online_dist].notnull()]
all = all[all[origin].notnull()]
all = all[all[destination].notnull()]
all = all.reset_index()
all = all.drop(['index'], axis = 1)



#calculating inorout
inout_dict = {"In": 'Terminating',
              "Out": "Originating",
              "Bridge" : 'unknown',
              'Empty': 'unknown',
              'Local': 'Originating',
              "LOCAL": "Originating",
              'Received': 'Terminating',
              'Operating': 'unknown',
              'ORIGINATING': 'Originating',
              "TERMINATING": "Terminating",
              "Forwarded": 'Originating',
              '': 'unknown',
              'Inbound': 'Terminating',
              'Outbound': "Originating",
              'ORIGINATE': 'Originating',
              'TERMINATE': 'Terminating',
            'Local': 'Originating',
              }
all.inout = all.inout.map(inout_dict)

#all.to_csv("apple.csv")

all.loc[np.isnan(all[total_wt]), total_wt] = all[no_of_cars]*all[wt_per_car] #important np.nan !=np.nan
#all.drop([no_of_cars,wt_per_car],axis=1, inplace=True)
#all.drop([no_of_cars,wt_per_car],axis=1, inplace=True)
all = all[all.wt >0]
all = all.reset_index()

conv_df = pd.read_csv("conversion.csv")



live_dict = {}
for i in range(len(conv_df)):
    live_dict[conv_df['Unnamed: 0'][i].strip().upper()] = [conv_df['0'][i], conv_df['1'][i], conv_df['2'][i]]

for i in range(len(all)):
    try:
        already_int = int(all.at[i, commodity])
        continue
    except:
        #not an integer
        not_int = all.at[i, commodity]
        print "'{0}' is not an integer, working...".format(not_int.strip().upper())
        all.at[i, commodity] = live_dict[not_int.strip().upper()][1]


# martland commodity list
mart_conv_dict = {
    #from table
    20: 1,  # food and kindred products
    371: 1,  # motor vehicles and equipments
    113: 2,  # farm products except grain
    26: 2,  # pulp&paper products
    32: 2,  # stone, clay & glass
    24: 3,  # lumbar or wood products
    1: 3,  # metal & products (confirm this code)
    8: 4,  # chemicals
    28: 4,  # petroleum products
    299: 5, # coke
    142: 5,  # crushed stone
    40: 5,  # sand and gravel
    144: 5,  # grain
    29: 5,  # waste and scrap
    11: 6,  # coal
    10: 6,  # metallic ores
    #put non metallic minerals here
    42: 1,  # Containers, Devices, Carriers, Returned Empty (changed from 7 to 1)
    421: 1,  # containers

    #from previous
    37422: 1,  # FREIGHT TRAIN CAR
    35: 1,  # Machinery (except electrical)
    36: 1,  # Electrical Machinery Equipment or Supplies

    30:1, # plastic products
    39:1, # Miscellaneous products of manufacturing
    41:1,   # Miscellaneous Freight

    44:1, # Freight Forwarder Traffic
    46:1, # FAK
    37:1, # Transportation Equipments
    #204: 1,  # grain mill products
    22:2, # textile
    34: 3,  # fabricated metal products
    33: 3,  # primary metal products
    49:2, # hazardous chemicals
    48:5, # hazardous waste

}


# martland commodity list
stcg_conv_dict = {


    # from table
    134:03 ,# agriculture products
    9: 5,   # Meat, Poultry, Fish, Seafood and their preparations

    8: 20,  # chemicals..
    142: 5, # crushed stone
    28: 20, #chemicals or allied products =-> basic chemicals
    131: 16, #crude petroleum --> crude petroleum
    10:14, #metallic ores
    11: 15, #coal
    1311: 16, #crude petroleum
    1321:-99,
    142: 12, #crushed or broken stone except dolomite or slate
    144: 12, #gravel or sand
    145: -99,
    147:
    20: 1,  # food and kindred products ????
    371: 1, # motor vehicles and equipments
    113: 2, # farm products except grain
    26: 2,  # pulp&paper products
    32: 2,  # stone, clay & glass
    24: 3,  # lumbar or wood products

    28: 4,  # petroleum products
    299: 5, # coke

    40: 5,  # sand and gravel
    144: 5, # grain
    29: 5,  # waste and scrap
    10: 6,  # metallic ores
    #put non metallic minerals here
    42: 1,  # Containers, Devices, Carriers, Returned Empty (changed from 7 to 1)
    421: 1, # containers


    # from previous
    37422: 1,  # FREIGHT TRAIN CAR
    35: 1,  # Machinery (except electrical)
    36: 1,  # Electrical Machinery Equipment or Supplies


    30:1,  # plastic products
    39:1,  # Miscellaneous products of manufacturing
    41:1,  # Miscellaneous Freight


    44:1,  # Freight Forwarder Traffic
    46:1,  # FAK
    37:1,  # Transportation Equipments
    # 204: 1,  # grain mill products
    22:2,  # textile
    34: 3, # fabricated metal products
    33: 3, # primary metal products
    49:2,  # hazardous chemicals
    48:5,  # hazardous waste

}




def get_commo(name):
    str_name = str(name)
    for i in range(len(str_name)+1):
        try:
            return mart_conv_dict[int(str_name)]
        except:
            str_name = str_name[:-1]
    return 0


commo_new = 'cmdtymrt'
all[commo_new] = ''

for i in range(len(all)):
        try:
            all.at[i, commo_new] = get_commo(all[commodity][i])
        except:
            print "Not found"
            print all.at[i, commodity]


# save it to a csv file
#drop stupid columns
all.drop(['index'],axis=1, inplace=True)

all.to_csv('shortline_output.csv')