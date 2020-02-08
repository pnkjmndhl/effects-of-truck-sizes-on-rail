import pandas as pd
import numpy as np
import re
from difflib import SequenceMatcher


def jaccard_similarity(str1, str2):
    intersection = len(list(set(str1).intersection(str2)))
    union = (len(str1) + len(str2)) - intersection
    return float(intersection) / union




#the file that was downloaded from the website
conv_DF = pd.read_csv("commodity_conver.csv")
conv_dict = dict(zip(conv_DF['Name'].tolist(), conv_DF['STCC'].tolist()))
conv_dict = {x.strip():y for x,y in conv_dict.iteritems()}
#opp_conv_dict = {v:k for k, v in conv_dict.iteritems()}


#this dictionary contains the conversion of string to STCC live (added from a csv file)
dumm = pd.DataFrame.from_csv("conversion.csv")
#dumm['new'] = "(" + dumm['index'] +"," + dumm['Unnamed: 1'] + ")"
#dumm.drop(['index', 'Unnamed: 1'], axis = 1, inplace = True)
#dumm  = dumm.set_index("new")
dumm1 = dumm.transpose().to_dict()
dumm2 = {x:[y['0'], int(y['2']), float(y['1'])] for x,y in dumm1.iteritems()}
conv_dict_live = dumm2






#now its first taken from the commodity conversion csv file

#retrieve
dumm = pd.DataFrame.from_csv("commodity_conver.csv")
#dumm['new'] = "(" + dumm['index'] +"," + dumm['Unnamed: 1'] + ")"
#dumm.drop(['index', 'Unnamed: 1'], axis = 1, inplace = True)
#dumm  = dumm.set_index("new")
dumm1 = dumm.transpose().to_dict()
dumm2 = {x:int(y['STCC']) for x,y in dumm1.iteritems()}
conv_dict = dumm2


#enter any string to this function, it would spit out the STCC code
def get_value(commodity_str):
    print ""
    commodity_str = commodity_str.upper()
    print "working on {0}".format(commodity_str)
    if commodity_str in conv_dict_live.keys():
        return conv_dict_live[commodity_str][1]
    else:
        match_list = {}
        commodity_str1= re.sub('[0-9, ]+', '', commodity_str)
        #always start with the specified str
        found_stcc = filter(re.compile("^"+".*".join(commodity_str1)+".*").search, conv_dict.keys())
        found_stcc.extend(filter(re.compile(".*"+"".join(commodity_str1)+".*").search, conv_dict.keys()))
        if found_stcc is not None:
            if len(found_stcc) in range(2,500):
                #print ""
                #print(commodity_str)
                i=0
                for stcc in found_stcc:
                    print "{0}: {1}".format(i,stcc)
                    i = i+1
                index = int(raw_input('Enter Index: (-1 to set default) '))
                if index != -1:
                    conv_dict_live[commodity_str] = [found_stcc[index], 2]
                    return found_stcc[0]
                else:
                    conv_dict_live[commodity_str] = [found_stcc[index], -1]
                    return 0
            elif len(found_stcc)==1:
                conv_dict_live[commodity_str] = [found_stcc[0], 2]
                return found_stcc[0]
        else:
            print "{0}: not found".format(commodity_str)
            for _str_ in conv_dict.keys():
                match_list[_str_]=SequenceMatcher(None, _str_, commodity_str).ratio()
            #max_match =  max(match_list, key=match_list.get)
            max_match_metric = max(match_list.values())  # maximum value
            max_metric_name = [k for k, v in match_list.iteritems() if v == max_match_metric][0]
            #max_match = opp_conv_dict[max_metric_name]
            conv_dict_live[commodity_str]=[max_metric_name,max_match_metric]
            print "{0}->{1}".format(commodity_str, max_metric_name)
            return max_metric_name


def is_number(n):
    try:
        float(n)   # Type-casting the string to `float`.
                   # If string is not a valid `float`,
                   # it'll raise `ValueError` exception
    except ValueError:
        return False
    return True


#all shortline_output
DF = pd.read_csv('remaining.csv').reset_index()


#create and modify the dictionary
for i in range(len(DF)):
    print get_value(DF['name'].iloc[i])



bad_matches = {x:y for x,y in conv_dict_live.iteritems() if y[1]<0.9}
good_matches = {x:y for x,y in conv_dict_live.iteritems() if y[1]>0.9}


#work on bad matches manually
pd.DataFrame({x: bad_matches[x] for x in bad_matches.keys()}).transpose().to_csv("dfdf.csv")


for x,y in remaining.iteritems():
    print '{0}->{1}'.format(x,y)


conv_dict_live_manual = {x:y for x,y in conv_dict_live.iteritems() if y[1] in [2,-1]}
conv_dict_live = conv_dict_live_manual

pd.DataFrame.from_dict(empty_dict, orient='index').to_csv("apple.csv")


remaining = {x:y for x,y in conv_dict_live.iteritems() if y[1] not in [2,-1]}

backup = conv_dict_live
conv_dict_live = backup

# conv_dict_live_stcc = {x: [y[0],y[1],conv_dict[y[0]]] for x,y in conv_dict_live.iteritems()}
#
# for x,y in conv_dict_live.iteritems():
#     try:
#         conv_dict_live_stcc[x] = [y[0],y[1],conv_dict[y[0]]]
#     except:
#         print x


pd.DataFrame({x: conv_dict_live[x] for x in conv_dict_live.keys()}).transpose().to_csv("conversion1.csv")


# for key,values in conv_dict_live.iteritems():
#     if len(values)==2:
#         conv_dict_live[key] = [values[0],conv_dict[values[0]], values[1] ]



df = pd.read_csv("dfdf.csv")


live_dict = {}
for i in range(len(df)):
    live_dict[df['Unnamed: 0'][i]] = [df['0'][i],df['1'][i]]
