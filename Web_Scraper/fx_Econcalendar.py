# -*- coding: utf-8 -*-
"""
Created on Sat Apr 11 16:43:43 2020

@author: quentinn.r.roby
"""

from bs4 import BeautifulSoup
import requests
import datetime
import logging
import csv
import pandas as pd
from datetime import date, timedelta
#import os
#from pathlib import Path
#path = str(Path(__file__).parent.absolute())
#path=path.replace("\\","\\\\")
#path=path[:path.find("WebScraper")]


DT = []
Currency = []
Impact =[]
Event = []
Actual = []
Forecast = []
Previous = []

class FXFactory_Connector:
    def setLogger():
        logging.basicConfig(level=logging.INFO, 
                            format = '%(asctime)s - %(levelname)s - %(message)s',
                            filename = 'logs_file',
                            filemode = 'w')
        console = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')      
        console.setFormatter(formatter)             
        logging.getLogger('').addHandler(console)
        
    def getEconomicCalendar(startlink, endlink):
        global DT
        global Currency
        global Impact
        global Event
        global Actual
        global Forecast
        global Previous
        
        # write to console current status
        logging.info("Scraping data for link: {}".format(startlink))
        
        # get the page and make the soup
        baseURL = "https://www.forexfactory.com/"
        r = requests.get(baseURL + startlink)
        print(r)
        data = r.text
        #print(data)
        soup = BeautifulSoup(data, "lxml")
        
        # get and parse table data, ignoring details and graph
        table = soup.find("table", class_="calendar__table")
        # do not use ".calendar__row--grey" css selector (reserved for historical data)
        trs = table.select("tr.calendar__row.calendar_row")
        fields = ["date","time","currency","impact","event","actual","forecast","previous"]
        
        # some rows do not have a date (cells merged)
        curr_year = startlink[-4:]
        curr_date = ""
        curr_time = ""
        
        for tr in trs:
            # fields may mess up sometimes, see Tue Sep 25 2:45AM French Consumer Spending
            # in that case we append to errors.csv the date time where the error is
            try:
                for field in fields:
                    data = tr.select("td.calendar__cell.calendar__{}.{}".format(field,field))[0]
                    #print(data)
                    
                    if field == "date" and data.text.strip()!="":
                        curr_date = data.text.strip()
                    elif field=="time" and data.text.strip()!="":
                        # time is sometimes "All Day" or "Day X" (eg. WEF Annual Meetings)
                        if data.text.strip().find("Day")!=-1:
                            curr_time = "12:00am"
                        else:
                            curr_time = data.text.strip()
                    elif field=="currency":
                        currency = data.text.strip()
                    elif field=="impact":
                        # when impact says "Non-Economic" on mouseover, the relevant
                        # class name is "Holiday", thus we do not use the classname
                        impact = data.find("span")["title"]
                    elif field=="event":
                        event = data.text.strip()
                    elif field=="actual":
                        actual = data.text.strip()
                    elif field=="forecast":
                        forecast = data.text.strip()
                    elif field=="previous":
                        previous = data.text.strip()
                     
                    
                    
                dt = datetime.datetime.strptime(",".join([curr_year,curr_date,curr_time]),
                                                "%Y,%a%b %d,%I:%M%p")
                
                #print(",".join([str(dt),currency,impact,event,actual,forecast,previous]))
                DT.append(dt)
                Currency.append(currency)   
                Impact.append(impact)
                Event.append(event)
                Actual.append(actual)
                Forecast.append(forecast)
                Previous.append(previous)
            
            except:
                with open("errors.csv","a") as f:
                    csv.writer(f).writerow([curr_year,curr_date,curr_time])
        
        # exit recursion when last available link has reached
        if startlink==endlink:
            logging.info("Successfully retrieved data")
            return(currency)
        
        # get the link for the next week and follow
        follow = soup.select("a.calendar__pagination.calendar__pagination--next.next")
        follow = follow[0]["href"]
        FXFactory_Connector.getEconomicCalendar(follow,endlink)
        
    def getImpactedCurrencies():
        df = pd.DataFrame({'DateTime': DT, 'Currency':Currency, 'Impact': Impact, 'Event': Event, 'Actual': Actual, 'Forecast': Forecast, 'Previous': Previous})
        df['Dates'] = pd.to_datetime(df['DateTime']).dt.date
        df['Time'] = pd.to_datetime(df['DateTime']).dt.time
        df2 = df[['Dates', 'Time', 'Currency', 'Impact', 'Event', 'Actual', 'Forecast', 'Previous']]
        df2 = df2.set_index('Dates')
        df2.to_csv('Forex_Calendar.csv')
        df3 = pd.read_csv('Forex_Calendar.csv')
        previousDate = date.today() - timedelta(days=1)
        previousDate = previousDate.strftime("%Y-%m-%d")
        nextDate = date.today() + timedelta(days=1)
        nextDate = nextDate.strftime("%Y-%m-%d") 
        mask = (df3['Dates'] >= previousDate) & (df3['Dates'] <= nextDate) & (df3['Impact'] == 'High Impact Expected')
        noTradeCurrencyList = df3.loc[mask]['Currency'].tolist()
        return noTradeCurrencyList
            

    


"""
Make the noTradeCurrencyList part of the logs for all trading bots. Use this below with the code above

noTradeCurrencyList
if string[0:3]+'_'+string[3:6] not in logs:
    Logic

"""



    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    