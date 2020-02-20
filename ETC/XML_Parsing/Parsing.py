import xml.etree.ElementTree as elemTree
import pandas as pd

b = input('원하는 xml파일 명을 입력하세요 : ')

tree = elemTree.parse(b)
root = tree.getroot()
Objects = root.findall('Objects')

a = {}
for child in root.iter('Object'):
    print(child.attrib['Type']+'_'+child.attrib['Instance'])
    for user in child:
        for property in user:
            if property.attrib == {'Id': 'PROP_OBJECT_NAME', 'Tag': 'BACNET_APPLICATION_TAG_CHARACTER_STRING'}: 
                for xx in property:
                    print(xx.text)
                    a[child.attrib['Type']+'_'+child.attrib['Instance']] = xx.text
       


result = pd.DataFrame(list(a.items()))
result.columns = ['PROP_OBJECT_NAME', 'BACNET_APPLICATION_TAG_CHARACTER_STRING']

print(a)

result.to_csv(b.replace('.xml', '_Parsing.csv'))