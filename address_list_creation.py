import arcpy
import os
from collections import Counter
import pandas as pd
import numpy as np
from ussolar.esri import FC_to_pandas
suffixes = ['JR','II', 'III', 'IV', 'VI', 'VII', 'SR', '3RD', '4TH']

gdb = r'C:\Users\NicholasRolstad\Documents\GitHub\residential_outreach\Markets\IL\ComEd\ComEd'
fc = 'postcards05262021'

arcpy.env.workspace = gdb

df = FC_to_pandas(os.path.join(r'C:\Users\NicholasRolstad\Documents\GitHub\residential_outreach\Markets\IL\ComEd\ComEd\Default.gdb',fc), fieldnames = None) # This shapefile should already have resi and service area queried out

def add_unique_address(c):
    return '{} {}'.format(c['MAIL_STREET'], c['MAIL_ZIP'])


def flag_non_unique_addresses(c, addy_count):
    if c['UNIQUE_ADDRESS'] in addy_count:
        return 1
    else:
        return 0
    
def add_pins(c):
    return "['{}']".format(c['SST_PIN'])

def get_first_last(c, suffixes):
    try:
        line = c['MAIL_NAME'].split()
        
        if line[1] == '&' or line[1] in suffixes:
            return [line[0].title(), line[-1].title()]
        else:
            return [line[0].title(), line[1].title()]
    except:
        return ['','']

def first_last(c, df):
    try:
        first, last = c['FL']
        df.loc[c.name, 'FIRST'] = first
        df.loc[c.name, 'LAST'] = last
    except:
        pass


df['UNIQUE_ADDRESS'] = df.apply(add_unique_address, axis=1)  # add field to identify addresses that appear multiple times
addy_list = []
for addy in df['UNIQUE_ADDRESS']:  # add all unique addresses to a list
    addy_list.append(addy)
    
addy_count = Counter(addy_list) # count how many times an address appears

for addy, count in addy_count.copy().items(): # delete the count addresses that only appear once
    if count == 1:
        del addy_count[addy]

#wx.CallAfter(frame.status_bar.SetStatusText,"UNIQUE ADDRESS MANAGEMENT")
df['NON_UNIQUE'] = df.apply(flag_non_unique_addresses, args=[addy_count], axis=1) # flag records where address appears more than once
df['ASSOCIATED_PINS'] = df.apply(add_pins, axis=1) # add all pins for 
non_unique_DF = df.loc[df['NON_UNIQUE'] == 1]
non_unique_addys = []
for addy in non_unique_DF['UNIQUE_ADDRESS']:
    if addy not in non_unique_addys:
        non_unique_addys.append(addy)
all_indices = []
for addy in non_unique_addys:
    temp_df = df.loc[df['UNIQUE_ADDRESS'] == addy]
    for index in temp_df.index.values:
        all_indices.append(index)
    longest_name = ''
    PIN_list = []
    for PIN in temp_df['SST_PIN']: # save all pins for a given address
        PIN_list.append(PIN)
    temp_df = temp_df.drop_duplicates(subset='OG_NAME_MAIL') # delete repeating records
    for name in temp_df['OG_NAME_MAIL']: # find longest name for a given address
        if len(name) > len(longest_name):
            longest_name = name
    largest_idx = temp_df.loc[temp_df['OG_NAME_MAIL'] == longest_name].index.values # get index of longest name value:
    for idx in largest_idx:
        df.loc[idx, 'ASSOCIATED_PINS'] = str(PIN_list)
        all_indices.remove(idx)

df['FL'] = df.apply(get_first_last, args=[suffixes], axis=1)
df.apply(first_last, args=[df], axis=1)

df.drop(df.index[all_indices], inplace=True)

df_out = pd.DataFrame()


df_out['PIN'] = df['SST_PIN']
df_out['RAW_NAME'] = df['OG_NAME_MAIL']
df_out['NAME'] = df['MAIL_NAME']
df_out['FIRST'] = df['FIRST']
df_out['LAST'] = df['LAST']
df_out['STREET'] = df['MAIL_STREET']
df_out['CITY'] = df['MAIL_CITY']
df_out['STATE'] = df['MAIL_STATE']
df_out['ZIPCODE'] = df['MAIL_ZIP']
df_out['COUNTY'] = df['SITE_COUNTY']
try:
    df_out['SST_SES'] = df['SocioEcon_Score']
except:
    print('no socioeconomic data')

try:
    df_out = df_out.sort_values(by=['SES'], ascending=False)
except:
    pass


df_out['NAME'].replace(' ', '', inplace=True)
df_out['NAME'].replace('', np.nan, inplace=True)
df_out.dropna(subset=['NAME'], inplace=True)

df_out['CITY'].replace(' ', '', inplace=True)
df_out['CITY'].replace('', np.nan, inplace=True)
df_out.dropna(subset=['CITY'], inplace=True)

df_out.to_csv('{}\Ameren_address_list_2021-05-26.csv'.format(gdb), index=False)






#df = df.drop_duplicates(subset=['brand'])


#df_out['PIN'] = df['SST_PIN']