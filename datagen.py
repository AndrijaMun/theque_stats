import sqlite3
import pandas as pd
import random
from datetime import datetime, timedelta

# generates a random time
def random_time():
    hour = random.randint(12, 22)
    if hour == 22:
        minute = random.randint(0, 30)
    else:
        minute = random.randint(0, 59)
    second = random.randint (0, 59)
    return hour, minute, second

# connecting to the database
conn = sqlite3.connect('theque.db')
cursor = conn.cursor()

# asks for the range of dates the user wants to generate data for
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

# inserts and sorts order dates and times
date = start_date
while date <= end_date:
    for _ in range(1, random.randint(4, 79)):
        hour, minute, second = random_time()
        date = datetime.combine(date, datetime.min.time()).replace(hour=hour, minute=minute, second=second)
        cursor.execute("""INSERT INTO Orders (OrderTime, OrderTypeID, StampCouponAmount) VALUES (?, ?, ?)""", (date, random.randint(1, 4), random.randint(1, 2)))
    date = date.replace(hour=0, minute=0, second=0)
    date += timedelta(days=1)
cursor.execute("""SELECT DISTINCT OrderTime FROM Orders ORDER BY OrderTime""")
sorted_data = [row[0] for row in cursor.fetchall()]
cursor.execute("""DELETE FROM Orders""")
for row in sorted_data:
    cursor.execute("""INSERT INTO Orders (OrderTime) VALUES (?)""", (row,))
conn.commit()



               