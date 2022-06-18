import pymssql
import json
import time
import requests
from time import sleep

# read and store local files
with open('device.json') as f:
    device = json.load(f)
with open('organization.json') as f:
    org = json.load(f)
# connect to database
conn = pymssql.connect('host', 'use', 'password', 'database')
cursor = conn.cursor(as_dict=True)
# read and store contacts list from db
cursor.execute('SELECT * FROM Contacts')
allContacts = cursor.fetchall()
# create new table for messages in db
query = 'CREATE TABLE SMS (DeviceKey NVARCHAR(32),AlarmType NVARCHAR(150), AlarMessage NVARCHAR(150), RecordTime datetime);'
cursor.execute(query)
conn.commit()
# set initial time
cursor.execute('SELECT TOP 1 RecordTime FROM Alarms ORDER BY RecordTime DESC')
old = cursor.fetchone()['RecordTime']

# send sms alert
def send_sms(dk,rt,dn,am):
    # sms content
    text = str(rt)+dn+am
    url = "SMS API url"
    # get org name
    orgID = next(item for item in device if item['DeviceKey']==dk)['OrgID']
    orgName = next(item for item in org if item['id']==orgID)['text']
    # get org contacts
    contacts = list(filter(lambda c: c['UserOrg']==orgName,allContacts))
    for c in contacts:
        data = {'Uid':'id','key':'key','Mobile':c['TelNo'],'Text':text)
        requests.post(url=url,data=data)

# check for device malfunctions
while True:
    # check every two min
    time.sleep(120)
    # get latest update
    cursor.execute('SELECT TOP 1 RecordTime FROM Alarms ORDER BY RecordTime DESC')
    new = cursor.fetchone()['RecordTime']
    # if new data
    if new > old:
        # read new data
        query = 'SELECT * FROM Alarms WHERE RecordTime BETWEEN %s AND %s;'
        cursor.execute(query, (old, new))
        rows = cursor.fetchall()
        for r in rows:
            dk = r['DeviceKey']
            at = r['AlarmType']
            am = r['AlarmMessage']
            rt = r['RecordTime']
            dn = r['DeviceName']
            # check if alert has been sent
            query = 'SELECT * FROM SMS WHERE (DeviceKey = %s AND AlarmType = %s AND AlarmMessage = %s);'
            cursor.execute(query,(dk,at,am))
            exist = cursor.fetchone()
            # if alert has been sent
            if exist:
                # if last alert was sent more than two hours ago
                old_rt = exist['RecordTime']
                if((rt-old_rt).total_seconds()>7200):
                    # update SMS table in db and resend alert
                    query = 'UPDATE SMS SET RecordTime = %s WHERE (DeviceKey = %s AND AlarmType = %s AND AlarmMessage = %s);'
                    cursor.execute(query,(rt,dk,at,am))
                    conn.commit()
                    send_sms(dk,rt,dn,am)
            # if no alert has been sent
            else:
                # update SMS table and send alert
                query = 'INSERT INTO SMS VALUES (%s,%s,%s,%s);'
                cursor.execute(query,(dk,at,am,rt))
                conn.commit()
                send_sms(dk,rt,dn,am)

    old = new

conn.close()
