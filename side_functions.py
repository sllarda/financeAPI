import re
import json
import requests
from bs4 import BeautifulSoup


def fixCharacters(text):
    turkish_letters = "çğıöşüÇĞİÖŞÜ"
    foreign_letters = "cgiosuCGIOSU"
    
    for i in range(len(turkish_letters)):
        text = text.replace(turkish_letters[i], foreign_letters[i])
    
    text = re.sub(r'[()\-\+]', '', text)
    
    return text.strip().lower()
    
def fixValues(value):
    cleaned_value = value.replace('₺', '').replace('.', '').replace(',', '.')
    float_value = float(cleaned_value)
    
    return float_value
    
def removeSymbols(value):
    return value.replace('%', '').replace('₺', '')
    
def commaToDot(value):
    newVal = value.replace(',', '.')
    return float(newVal)
    
def getCompanyName(company):
    words = company.split(' - ')
    return words[1].strip()
    
# table functions

def getKeysAndValues(value, years):
    tableData = []
    
    data = {
        "finansal_tablolar": {
            "bilanco": {
                
            },
            
            "gelir_tablosu": {
                
            },
            
            "nakit_akim_tablosu": {
                
            }
        }
    }
    
    for tag in value:
        control = tag.get('colspan')
        if control == "5":
            value.remove(tag)
        
    for tag2 in value:
        tableData.append(tag2)
    
    
    target_table = "bilanco"
    for a in range(0, len(tableData), 5):
        items = value[a:a+5]
        values = []
        
        for b in items[1:]:
            values.append(int(fixValues(b.string)))
        
            
        data["finansal_tablolar"][target_table].update({
            fixCharacters(items[0].string): {
                years[-1]: values[0],
                years[-2]: values[1],
                years[-3]: values[2],
                years[-4]: values[3],
            }
        })
        
        if fixCharacters(items[0].string) == "toplam kaynaklar":
            target_table = 'gelir_tablosu'
        if fixCharacters(items[0].string) == "surdurulen faaliyetlerden seyreltilmis hisse basina kazanc":
            target_table = 'nakit_akim_tablosu'
        
    
    return data
    
def controlCompany(symbol):
    try:
        url = f'https://www.getmidas.com/canli-borsa/{symbol}-hisse/'
        response = requests.get(url)
        html = response.content
        soup = BeautifulSoup(html, 'html.parser')
        
        company = soup.find('h1').string
        
    except Exception:
        return False