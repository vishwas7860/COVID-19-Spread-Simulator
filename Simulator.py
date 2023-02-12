import pandas as pd
import datetime
import random
import numpy as np
import sim_parameters
import helper
from dateutil import parser
from pathlib import Path
import os


def days_calculator(begin, finish):
    
    begin = list(begin)
    begin[5:7], begin[8:] = begin[8:], begin[5:7]
    begin = ''.join(begin)
    finish = list(finish)
    finish[5:7], finish[8:] = finish[8:], finish[5:7]
    finish = ''.join(finish)
    
   
    dttt = parser.parse(begin, dayfirst=True)
    
    day_collection = [dttt.date()]
   
    while True:
        
        if dttt != parser.parse(finish, dayfirst=True):
            
            dttt = dttt + datetime.timedelta(days=1)
            
            day_collection.append(dttt.date())
        else:
            
            break
    
    return day_collection


def get_Matrix(TRASITION_PROBS):
    
    transitionName = [[f + ff for ff in TRASITION_PROBS["5_to_14"]] for f in TRASITION_PROBS["5_to_14"]]
    
    transitionMatrix = [[0.0 for ee in range(len(TRASITION_PROBS["5_to_14"]))] for e in
                        range(len(TRASITION_PROBS["5_to_14"]))]
    
    for k, ro in enumerate(transitionName):
        
        for l, co in enumerate(ro):
            
            if co[1] in TRASITION_PROBS["5_to_14"][co[0]]:
                
                transitionMatrix[k][l] = TRASITION_PROBS["5_to_14"][co[0]][co[1]]
    
    return transitionName, transitionMatrix


def ageGroup_iterator(state, dates_list, df, old_df, num_days, prepp_id, cube, age_division, HTtt, transit_Name, transit_Matrix,
                      sample_ratio):
    
    temprary_pop = (df[df["country"] == cube]["population"]) / int(sample_ratio)
    
    age_division_actual_pop = int(temprary_pop * (df[df["country"] == cube][age_division]) / 100)
    
    for PER_ID in range(age_division_actual_pop):
      
        ppp_id = [PER_ID + prepp_id] * num_days
        
        countrie = [cube] * num_days
        
        a_division = [age_division] * num_days
        
        situation_Today = state[0]
        
        iterate_loop, prob, st, sd, ag, ps = 0, 1, [], [], [], []
        
     
        while iterate_loop < num_days:
            
            ps.append(situation_Today)
            
            indx_number = state.index(situation_Today)
            
            gapping = num_days - 1 - iterate_loop
            
            iterate_loop1 = 0
            if gapping >= HTtt[state[indx_number]]:
                while iterate_loop1 < HTtt[state[indx_number]]:
                    
                    ps.append(situation_Today)
                    
                    sd.append(HTtt[state[indx_number]] - iterate_loop1)
                    
                    st.append(situation_Today)

                    iterate_loop1 += 1
                    iterate_loop += 1

            else:
                while iterate_loop1 < gapping:
                    
                    ps.append(situation_Today)
                    
                    sd.append(HTtt[state[indx_number]] - iterate_loop1)
                    
                    st.append(situation_Today)
                    iterate_loop1 += 1
                    iterate_loop += 1
            
            change_value = np.random.choice(transit_Name[indx_number], replace=True, p=transit_Matrix[indx_number])
            
            if change_value[0] == change_value[1]:
               
                indx_number1 = transit_Name[indx_number].index(change_value)
               
                prob = prob * transit_Matrix[indx_number][indx_number1]
                pass
            else:
                
                indx_number1 = transit_Name[indx_number].index(change_value)
                
                prob = prob * transit_Matrix[indx_number][indx_number1]
                
                situation_Today = change_value[1]
            
            st.append(situation_Today)
            
            sd.append(0)

            iterate_loop += 1
      
        data = list(zip(ppp_id, a_division, countrie, dates_list, st, sd, ps))
      
        temp_df1 = pd.DataFrame(data, columns=['id', 'age_group_name', 'country', 'date', 'state', 'staying_days',
                                               'pre_state'])
        
        old_df = pd.concat([old_df, temp_df1])
        
        old_df.reset_index(drop=True, inplace=True)
  
    prepp_id += age_division_actual_pop
    
    return old_df, prepp_id


def country_iterator(state, dates, df, old_df, days, prepp_id, cube, sample_ratio, TRASITION_PROBS, HOLDING_TIMES):
    transit_Name, transit_Matrix = get_Matrix(TRASITION_PROBS)

    for age_division in TRASITION_PROBS:
        HTtt = HOLDING_TIMES[age_division]
        old_df, prepp_id = ageGroup_iterator(state, dates, df, old_df, days, prepp_id, cube, age_division, HTtt, transit_Name,
                                             transit_Matrix, sample_ratio)
    return old_df


def country(df2, dictt, date, get_state, countries):
    
    for c in countries:
        
        dictt["date"].append(date)
        
        dictt["country"].append(c)
        
        data = df2[df2["date"] == date]
        
        data1 = data[data["country"] == c]
        
        for s in get_state:
            
            data2 = data1[data1["state"] == s]
            
            if s == "H":
                dictt["H"].append(len(data2))
            
            elif s == "M":
                dictt["M"].append(len(data2))
           
            elif s == "S":
                dictt["S"].append(len(data2))
           
            elif s == "D":
                dictt["D"].append(len(data2))
            
            else:
                dictt["I"].append(len(data2))
    return dictt


def dates_iterator(dates, df2, get_state, countries, dictt):
    for date in dates:
        dictt = country(df2, dictt, date, get_state, countries)
    return dictt


def run(countries_csv_name, countries, sample_ratio, start_date, end_date):
    df = pd.read_csv(countries_csv_name)
    TRASITION_PROBS = sim_parameters.TRASITION_PROBS
    HOLDING_TIMES = sim_parameters.HOLDING_TIMES

    df2 = pd.DataFrame()
    
    dates = days_calculator(start_date, end_date)
    
    days = len(dates)
    
    state = "HISDM"
    
    pre_id = 0

    
    for cn in countries:
        
        df2 = country_iterator(state, dates, df, df2, days, pre_id, cn, sample_ratio, TRASITION_PROBS, HOLDING_TIMES)
    
    dictt = {"date": [],
             "country": [],
             "D": [],
             "H": [],
             "I": [],
             "M": [],
             "S": []
            }
    
    
    data = dates_iterator(dates, df2, state, countries, dictt)
   
    df = pd.DataFrame(data)

    df.to_csv("covid-summary-timeseries.csv", index=False)
    df1 = df.iloc[:,[1,0,2,3,4,5,6]]
    df1.to_csv("summary.csv", index=False)
    df2.to_csv("covid-simulated-timeseries.csv", index=False)
    helper.create_plot("summary.csv", countries)
