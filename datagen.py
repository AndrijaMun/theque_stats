import sqlite3
import pandas as pd
import random
from datetime import datetime, timedelta

def random_time():
    hour = random.randint(12, 22)
    if hour == 22:
        minute = random.int(0, 30)
    else:
        minute = random.int(0, 59)
    second = random.randint (0, 59)
    return datetime.now().replace(hour=hour, minute=minute, second=second)

random_time_obj = 0
daily_orders = 0
counter = 0

conn = sqlite3.connect('schemagen.sql')
cursor = conn.cursor()

while True:
    try:
        start_date, end_date = [
            datetime.strptime(date_str, '%Y-%m-%d')
            for date_str in input("Enter starting and ending dates for traffic data (YYYY-MM-DD YYYY-MM-DD): ").split()
        ]

        if start_date > end_date:
            print("INVALID INPUT: start date must be before or same as end date")
        else:
            break

    except ValueError:
        print("INVALID INPUT: formatting error")

date = start_date
while date <= end_date:
    daily_orders = random.randint(5, 80)
    counter = 1
    while counter <= daily_orders:
        random_time_obj = random_time()
        date = date.replace(hour=random_time_obj.hour, minute=random_time_obj.minute, second=random_time_obj.second)
        if date == cursor.execute("""SELECT OrderTime FROM Orders WHERE OrderID = (SELECT MAX(OrderID) - 1 FROM Orders"""):
            date += timedelta(seconds=30)
        cursor.execute("""INSERT INTO Orders (OrderTime) VALUES (?)""", date)
        counter += 1
    date += timedelta(days=1)
cursor.execute("""SELECT OrderTime FROM Orders ORDER BY datetime_column""")