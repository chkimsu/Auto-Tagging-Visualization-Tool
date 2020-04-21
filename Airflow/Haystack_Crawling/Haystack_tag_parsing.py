from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import re

html = urlopen('https://project-haystack.org/tag')
bsObject = BeautifulSoup(html, 'html.parser')

def remove_tag(content):
    cleanr =re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', content)
    return cleantext
    
tag = []
for i in range(0, len(bsObject.find_all('td')),2):
    tag.append(remove_tag(str(bsObject.find_all('td')[i])))
    
tagframe = pd.DataFrame(tag)


doc = bsObject.find_all('p')
content = []
for i in range(len(doc)):
    content.append(re.sub('<.+?>','',str(doc[i]),0).strip())
    
content = content[:-1]   ## 마지막에 license 제외해줘야 한다. 
contentframe = pd.DataFrame(content)

result = pd.concat([tagframe, contentframe], axis=1)
result.columns = ['tag', 'content']


result.to_csv('tag-content.csv')