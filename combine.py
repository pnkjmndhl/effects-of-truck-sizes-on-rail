import pandas
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

# extract from excel files
ACWR = pandas.ExcelFile("./CARRIER_DATA2/ACWR.xlsx").parse("Sheet1")
AGR_BPRR = pandas.ExcelFile("./CARRIER_DATA2/AGR_BPRR.xlsx").parse("Sheet1")
FMRC = pandas.ExcelFile("./CARRIER_DATA2/FMRC.xlsx").parse("Sheet1")
GNBC = pandas.ExcelFile("./CARRIER_DATA2/GNBC.xlsx").parse("Sheet1")
INRR = pandas.ExcelFile("./CARRIER_DATA2/INRR.xlsx").parse("Sheet1")
KYLE = pandas.ExcelFile("./CARRIER_DATA2/KYLE.xlsx").parse("Sheet1")
WSOR = pandas.ExcelFile("./CARRIER_DATA2/WSOR.xlsx").parse("Sheet1")
YSVR = pandas.ExcelFile("./CARRIER_DATA2/YSVR.xlsx").parse("Sheet1")

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

acwr = acwr.drop(['In Out', 'Chrg Patron Id', 'Chrg Rule 260 Cd', 'Interline Off-Line O/D', 'Onl Patron Station Name'],
                 axis=1)
acwr['rr'] = 'acwr'
acwr = acwr.rename(columns={'Sum of Num Of Cars': no_of_cars, 'Median Weight': wt_per_car, 'Commodity': commodity,
                            'Median Mileage from Station to Interchange': online_dist, 'rr1': start_rr,
                            'rr': current_rr, 'rr2': forwarded_rr,
                            'o1': transfer_1, 'd1': transfer_2, 'origin': origin, 'dest': destination})

# done


# preparing AGR_BPRR data
agr = AGR_BPRR
agr = agr[['2017Total Cars', 'Average Net Weight', 'STCC Description', 'Interchange Road From', 'City Trip Start',
           'State Trip Start', 'City Trip End', 'State Trip End',
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
    columns={'2017Total Cars': no_of_cars, 'Average Net Weight': wt_per_car, 'STCC Description': commodity,
             'Average TMS Miles': online_dist, 'Interchange Road From': start_rr, 'Railroad Id': current_rr,
             'Interchange Road To': forwarded_rr,
             'start': transfer_1, 'end': transfer_2, 'WB Origin': origin, 'WB Destination': destination})

# agr.to_csv("agr.csv")

# done

# preparing FMRC data
fmrc = FMRC
fmrc['On-Line O/D'] = fmrc['On-Line O/D'] + ", OK"
fmrc['Interchange Location'] = fmrc['Interchange Location'] + ", OK"

for i in range(len(fmrc)):
    if fmrc['Inbound or Outbound or Bridge'].iloc[i] == 'Inbound':
        fmrc.at[i, 'rr1'] = fmrc['Interchange Railroad'].iloc[i]
        fmrc.at[i, 'o1'] = fmrc['Interchange Location'].iloc[i]
        fmrc.at[i, 'origin'] = fmrc['Off-Line O/D'].iloc[i]
        fmrc.at[i, 'destination'] = fmrc['On-Line O/D'].iloc[i]
    elif fmrc['Inbound or Outbound or Bridge'].iloc[i] == 'Outbound':
        fmrc.at[i, 'rr2'] = fmrc['Interchange Railroad'].iloc[i]
        fmrc.at[i, 'd1'] = fmrc['Interchange Location'].iloc[i]
        fmrc.at[i, 'origin'] = fmrc['On-Line O/D'].iloc[i]
        fmrc.at[i, 'destination'] = fmrc['Off-Line O/D'].iloc[i]
    else:
        fmrc.at[i, 'rr2'] = np.nan
        fmrc.at[i, 'd1'] = np.nan
        fmrc.at[i, 'origin'] = np.nan
        fmrc.at[i, 'destination'] = np.nan
        fmrc.at[i, 'rr1'] = np.nan
        fmrc.at[i, 'o1'] = np.nan

fmrc = fmrc.drop(
    ['Inbound or Outbound or Bridge', 'Off-Line O/D', 'On-Line O/D', 'Interchange Location', 'Interchange Railroad',
     "Local O/D", "Seasonality"], axis=1)  # seasonality could be added later
fmrc['rr'] = 'fmrc'
fmrc = fmrc.rename(
    columns={'2017 Carloads': no_of_cars, 'Typical Net (Lading) Weight per Car': wt_per_car, 'Commodity': commodity,
             'Online Shipment Distance': online_dist, 'rr1': start_rr, 'rr': current_rr, 'rr2': forwarded_rr,
             'o1': transfer_1, 'd1': transfer_2, 'origin': origin, 'dest': destination})

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

gnbc = gnbc.drop(['online_od', 'offline_od', 'Inbound or Outbound or Bridge', 'On-Line O/D County', 'On-Line O/D State',
                  'Off-Line O/D County', 'Off-Line O/D State', 'Interchange Location', 'Interchange Railroad',
                  "Local O/D", "Seasonality", 'On-Line O/D', 'Off-Line O/D', 'Unnamed: 15'],
                 axis=1)  # seasonality could be added later
gnbc['rr'] = 'gnbc'
gnbc = gnbc.rename(
    columns={'2017 Carloads': no_of_cars, 'Typical Net (Lading) Weight per Car': wt_per_car, 'Commodity': commodity,
             'Online Shipment Distance': online_dist, 'rr1': start_rr, 'rr': current_rr, 'rr2': forwarded_rr,
             'o1': transfer_1, 'd1': transfer_2, 'origin': origin, 'dest': destination})

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
    ['On-Line O/D', 'Off-Line O/D', 'Interchange Location', 'Interchange Railroad', 'Inbound or Outbound or Bridge'],
    axis=1)
inrr['rr'] = 'inrr'
inrr = inrr.rename(
    columns={'2017 Carloads': no_of_cars, 'Typical Net (Lading) Weight per Car': wt_per_car, 'Commodity': commodity,
             'Online Shipment Distance': online_dist, 'rr1': start_rr, 'rr': current_rr, 'rr2': forwarded_rr,
             'o1': transfer_1, 'd1': transfer_2, 'origin': origin, 'dest': destination})
# done

# preparing KYLE
kyle = KYLE
kyle = kyle[
    ['Interchange Road From', 'Interchange Road To', 'STCC Description', 'Net Weight', 'Station Name Trip Start',
     'State Trip Start', 'Station Name Trip End', 'State Trip End', 'TMS Miles', 'Number of Cars', 'WB Origin',
     'WB Destination']]
kyle['o1'] = kyle['Station Name Trip Start'] + ', ' + kyle['State Trip Start']
kyle['d1'] = kyle['Station Name Trip End'] + ', ' + kyle['State Trip End']
kyle = kyle.drop(['Station Name Trip Start', 'State Trip Start', 'Station Name Trip End', 'State Trip End'], axis=1)
kyle = kyle.rename(columns={'Number of Cars': no_of_cars, 'Net Weight': wt_per_car, 'STCC Description': commodity,
                            'TMS Miles': online_dist, 'Interchange Road From': start_rr, 'rr': current_rr,
                            'Interchange Road To': forwarded_rr, 'WB Origin': origin, 'WB Destination': destination})
kyle = kyle.replace('Missing', np.nan)
kyle['rr'] = 'kyle'

# done


# preparing WSOR
# problems: where are the location of transfers gonna be?
# need to work on "Road & Junctions", the final or first taken
wsor = WSOR
# the bridge data has 0 tons so removed
wsor = wsor[wsor['IB/OB'] != 'BRIDGE']
# wsor = wsor.dropna() #removing "Total" calculated in the excel file, lets not be that aggressive
wsor = wsor.drop(['Seasonality'], axis=1)
for i in range(len(inrr)):
    if wsor['IB/OB'].iloc[i] == 'In':
        wsor.at[i, 'rr1'] = wsor['Road & Junctions'].iloc[i].split(' ')[0]
        wsor.at[i, 'o1'] = np.nan
    elif wsor['IB/OB'].iloc[i] == 'Out':
        try:
            wsor.at[i, 'rr2'] = wsor['Road & Junctions'].iloc[i].split(' ')[1]
        except:
            wsor.at[i, 'rr2'] = np.nan
        wsor.at[i, 'd1'] = np.nan

wsor = wsor.drop(['D-Rd', 'IB/OB', 'O-Rd', 'Road & Junctions'], axis=1)
wsor = wsor.rename(columns={'Sum of Total Cars': no_of_cars, 'Average of Tons': wt_per_car, 'Description': commodity,
                            'Average of Miles2': all_dist, 'rr1': start_rr, 'rr': current_rr,
                            'Destination	D-Rd': forwarded_rr, 'o1': transfer_1, 'd1': transfer_2, 'Origin': origin,
                            'Destination': destination})
wsor['rr'] = 'wsor'


# wsor.to_csv("wsor.csv")

# done


def get_rr1_rr2(listofrr):
    rrs = listofrr.split(",")
    for i in range(4):
        try:
            rrs.remove("    ")
        except:
            pass
    try:
        index_of_rr = rrs.index('YSVR')
    except:
        print("YSVR not in the list")
        index_of_rr = len(rrs) - 1
    if index_of_rr == 0:
        rr2 = rrs[1]
        rr1 = np.nan
    elif index_of_rr == len(rrs) - 1:
        rr1 = rrs[0]
        rr2 = np.nan
    else:
        rr1 = rrs[0]
        rr2 = rrs[index_of_rr + 1]
    try:
        rr1 = rr1.replace(" ", "")
    except:
        pass
    try:
        rr2 = rr2.replace(" ", "")
    except:
        pass
    return [rr1, rr2]


# preparing YSVR
# total weight given, weight per car not given
ysvr = YSVR[['COMMODITY DESC', 'ORIGIN', 'DEST', 'ROUTE ROAD 01', 'ROUTE ROAD 02', 'ROUTE ROAD 03', 'ROUTE ROAD 04',
             "ROUTE ROAD 05", "NET WEIGHT", "MILES"]]
ysvr['rrlist'] = [
    row['ROUTE ROAD 01'] + "," + row['ROUTE ROAD 02'] + "," + row['ROUTE ROAD 03'] + "," + row['ROUTE ROAD 04'] + "," +
    row['ROUTE ROAD 05'] for index, row in ysvr.iterrows()]
ysvr['rr1'] = ''
ysvr['rr2'] = ''
for i in range(len(ysvr)):
    ysvr.at[i, 'rr1'], ysvr.at[i, 'rr2'] = get_rr1_rr2(ysvr['rrlist'].iloc[i])

ysvr = ysvr.drop(["rrlist", 'ROUTE ROAD 01', 'ROUTE ROAD 02', 'ROUTE ROAD 03', 'ROUTE ROAD 04', "ROUTE ROAD 05"],
                 axis=1)
ysvr = ysvr.rename(columns={'Sum of Total Cars': no_of_cars, 'NET WEIGHT': total_wt, 'COMMODITY DESC': commodity,
                            'MILES': all_dist, 'rr1': start_rr, 'rr': current_rr,
                            'Destination	D-Rd': forwarded_rr, 'o1': transfer_1, 'd1': transfer_2, 'ORIGIN': origin,
                            'DEST': destination})

# ysvr.to_csv("ysvr.csv")


# adding all to one
all = wsor.append(acwr).append(agr).append(fmrc).append(gnbc).append(inrr).append(kyle).append(wsor).append(ysvr)

# all maths
# all = all[all[commodity].notnull()]
# all = all[all[no_of_cars].notnull()]
# all = all[all[wt_per_car].notnull()]
# all = all[all[online_dist].notnull()]
# all = all[all[origin].notnull()]
# all = all[all[destination].notnull()]


all.to_csv('sss.csv')
