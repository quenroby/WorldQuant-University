from bs4 import BeautifulSoup
import requests
import csv
import pandas as pd


times = []
currency = []
impact = []
event = []

class FXEconomic_Connector:
    
    def getEconomicCalendar():
        global times
        global currency
        global impact
        global event
        
        headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
        baseURL = "https://www.investing.com/economic-calendar/"
        #startlink = "calendar" 
        
        r = requests.get(baseURL, headers=headers)
        data = r.text
        soup = BeautifulSoup(data, "html.parser")
        times = [element.text for element in soup.find_all("td", "first left time js-time")]
        currencyTemp = [element.text for element in soup.find_all("td", "left flagCur noWrap")]
        currency = [item.replace("\xa0 ", "") for item in currencyTemp]
        
        
        table = soup.find("table", id="economicCalendarData", class_="genTbl closedTbl ecoCalTbl persistArea js-economic-table")
        row = table.find_all("tr")
        impactPlaceHolder = []
        for tr in row: 
            data = tr.select("td.left.textNum.sentiment.noWrap")
            impactPlaceHolder.extend(data)
        
        impactTemp = [str(i) for i in impactPlaceHolder]
        impact = [item.count('class="grayFullBullishIcon"') for item in impactTemp]
        
        
        eventTemp1 = [element.text for element in soup.find_all("td", "left event")]
        eventTemp2 = [item.replace("\n", "") for item in eventTemp1]
        event = [item.replace(" \xa0", "") for item in eventTemp2]
    
        
        
    def getImpactedCurrencies():
        df = pd.DataFrame({'Time': times, 'Currency': currency, 'Impact': impact})
        df2 = df.set_index('Time')
        #df2.to_csv('Forex_Calendar.csv')
        mask = df2['Impact'] == 3
        noTradeCurrencyList = df2.loc[mask]['Currency'].tolist()
        return noTradeCurrencyList
        
    
FXEconomic_Connector.getEconomicCalendar()
#FXEconomic_Connector.getImpactedCurrencies()
        
   
        







