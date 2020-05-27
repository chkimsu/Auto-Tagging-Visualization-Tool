import sys



import os
os.chdir('/data01/CSB/CSB_Jupyter/ATVT/Xml_parsing/')

import xml.etree.ElementTree as elemTree
import pandas as pd
pd.set_option('display.max_columns', 500)

tree = elemTree.parse(str(sys.argv[1])+'.xml')
root = tree.getroot()
Objects = root.findall('Objects')

a = {}
for child in root.iter('Object'):
    
    for user in child:
        for property in user:
            if property.attrib == {'Id': 'PROP_OBJECT_NAME', 'Tag': 'BACNET_APPLICATION_TAG_CHARACTER_STRING'}: 
                for xx in property:
                    
                    a[child.attrib['Type']+'_'+child.attrib['Instance']] = xx.text
       


result = pd.DataFrame(list(a.items()))
result.columns = ['PROP_OBJECT_NAME', 'BACNET_APPLICATION_TAG_CHARACTER_STRING']

import xml.etree.ElementTree as elemTree
import pandas as pd
 
tree = elemTree.parse(str(sys.argv[1])+'.xml')
root = tree.getroot()
Objects = root.findall('Objects')

a = {}
for child in root.iter('Object'):
    
    for user in child:
        for property in user:
            if property.attrib == {'Id': 'PROP_DESCRIPTION', 'Tag': 'BACNET_APPLICATION_TAG_CHARACTER_STRING'}: 
                for xx in property:
                    
                    a[child.attrib['Type']+'_'+child.attrib['Instance']] = xx.text
       


result2 = pd.DataFrame(list(a.items()))
result2.columns = ['PROP_OBJECT_NAME', 'BACNET_APPLICATION_TAG_CHARACTER_STRING']


import xml.etree.ElementTree as elemTree
import pandas as pd
 
tree = elemTree.parse(str(sys.argv[1])+'.xml')
root = tree.getroot()
Objects = root.findall('Objects')

a = {}
for child in root.iter('Object'):
    
    for user in child:
        for property in user:
            if property.attrib == {'Id': 'PROP_OBJECT_IDENTIFIER', 'Tag': 'BACNET_APPLICATION_TAG_OBJECT_ID'}: 
                for xx in property:
                    
                    a[child.attrib['Type']+'_'+child.attrib['Instance']] = xx.text
       


result3 = pd.DataFrame(list(a.items()))
result3.columns = ['PROP_OBJECT_IDENTIFIER', 'PROP_OBJECT_IDENTIFIER']


final = pd.concat([result3, result, result2], axis=1)
final = final.iloc[:, [0, 3,5]]
final.columns = ['PROP_OBJECT_IDENTIFIER', 'PROP_OBJECT_NAME', 'PROP_DESCRIPTION']
final.to_csv(str(sys.argv[1])+'_Parsing.csv')

print(final)