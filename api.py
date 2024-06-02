import requests
from bs4 import BeautifulSoup
import json
from side_functions import * # my own framework
import time


def scrapeMain(symbol):
    url = f'https://www.getmidas.com/canli-borsa/{symbol}-hisse/'
    
    print('\nŞirket bilgileri hazırlanıyor...')
        
    response = requests.get(url)
    html = response.content
    soup = BeautifulSoup(html, 'html.parser')
        
    company = soup.find('h1').string
    company = getCompanyName(company)
    company = fixCharacters(company)
    
    price = soup.find('p', class_='val').string
    price = price[1:]
    price = commaToDot(price)
        
    dailyChange = soup.find_all('p', class_='val')[2].string.strip()
    dailyChange = dailyChange.split(' ')[1]
    dailyChange = float(dailyChange.replace('%', '').replace('(', '').replace(')', ''))
        
    table = soup.find_all('span', class_='val')
        
    peRate = commaToDot(table[7].string.strip())
        
    marketValue = table[8].string.strip()
    marketValue = fixValues(marketValue)
        
    volatility = table[10].string.strip()
    volatility = removeSymbols(volatility)
    volatility = commaToDot(volatility)
        
    pddd = table[18].string.strip()
    pddd = commaToDot(pddd)
        
        
    main = {
        "sirket": company,
        "sembol": symbol.upper(),
        "fiyat": price,
        "gunluk_degisim": dailyChange,
        "f/k": peRate,
        "piyasa_degeri": marketValue,
        "volatilite": volatility,
        "pd/dd": pddd
    }
        
    return main
    
    
def scrapeTables(symbol):
    url = f'https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/sirket-karti.aspx?hisse={symbol}'
    
    print('Finansal tablolar hazırlanıyor...')
    
    response = requests.get(url)
        
    html = response.content
    soup = BeautifulSoup(html, 'html.parser')
            
    headers = soup.find_all('thead')
    tables = soup.find_all('tbody')
        
    for head in headers:
        option_tags = head.find_all('option')
        if len(option_tags) > 150 and len(option_tags) < 400:
            years = head.find_all('option', {'selected': 'selected'})
            years_value = []
                
            for year_tag in years:
                years_value.append(year_tag['value'])
            years = years_value
            break
        
        
    for table in tables:
        value_tags = table.find_all('td')
        if len(value_tags) > 700:
            values = value_tags
            break
            
            
    return getKeysAndValues(values, years)
    
    
def writeData(mainData, tablesData):
    print('Veriler kaydediliyor...')
    
    jsonData = {
        "genel_bilgiler": {
            
        }
    }
    
    jsonData["genel_bilgiler"].update(mainData)
    jsonData.update(tablesData)
    
    with open('financial_data.json', "w") as file:
        json.dump(jsonData, file, indent=4)
        
    print("\nŞirket bilgileri 'financial_data.json' adlı dosyaya eklendi!")



userInp = input('Şirketin Sembolü (örn: THYAO): ')

control = controlCompany(userInp)

if control == False:
    print(f"\n{userInp.upper()} sembolüyle şirket bulunamadı!")
else:
    mainSc = scrapeMain(userInp)
    tableSc = scrapeTables(userInp)
    time.sleep(2)
    writeData(mainSc, tableSc)