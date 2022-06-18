# Medical device monitor
This project was written for a hypothetical hospital.

The hospital has a list (json file) of 'devices' they need to monitor and a list of 'organizations' that should be contacted if any device malfunctions. The hospital also has a database (MSSQL) with two tables: 'Contacts' and 'Alarms'. 'Contacts' stores the names and phone numbers of supervisors in each organization. 'Alarms' stores the unique key and name of devices that have malfunctioned, the time the malfunction occurred, and the alerts that have been sent. 'Alarms' is automatically updated by equipments that monitor the devices.

The hospital needs an API that sends text messages to related supervisors once a device malfunctions. Resend text if the same malfunction still hasn't been fixed after two hours. 

The hospital prefers to have a separate table in the database to store all messages that have been sent.
