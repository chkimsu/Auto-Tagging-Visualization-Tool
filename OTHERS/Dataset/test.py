import pymysql
import pandas as pd
import csv
from glob import glob
from os.path import expanduser

# MySQL Connection 연결
conn = pymysql.connect(host='192.168.21.6', user='root', password='ntels',
                       db='nise', charset='utf8')

# Connection 으로부터 Cursor 생성
curs = conn.cursor()

# SQL문 실행c
sql = "select * from auto_tagging"
curs.execute(sql)

# 데이타 Fetch
rows = curs.fetchall()
print(rows)

with open("out.csv", "w", newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow([i[0] for i in curs.description]) # write headers
    csv_writer.writerows(rows)

# Connection 닫기
conn.close()