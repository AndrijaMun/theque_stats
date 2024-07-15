import os
import sqlite3
import pandas as pd
import random
from datetime import datetime, timedelta

# creating and connecting to the database
if os.path.exists('theque.db'):
    os.remove('theque.db')
conn = sqlite3.connect('theque.db')
cursor = conn.cursor()

# executing SQL within the database
with open('schemagen.sql', 'r') as sql_file:
    cursor.executescript(sql_file.read())
conn.commit()

# function that generates a random time
def random_time():
    hour = random.randint(12, 21)
    minute = random.randint(0, 59)
    second = random.randint (0, 59)
    return hour, minute, second

#function that sets shifts for cashiers
shift_offset = [1, 3]
offset1 = random.choice(shift_offset)
shift_offset.remove(offset1)
offset2 = shift_offset[0]
counter1 = offset1
counter2 = offset2
def set_shifts():
    global counter1, counter2, morning_shift, evening_shift, offset1, offset2
    options = [1, 2]
    morning_shift = random.choice(options)
    options.remove(morning_shift)
    evening_shift = options[0]
    if counter1 > 7:
        counter1 = 1
    elif counter1 > 5:
        if morning_shift == 1:
            morning_shift = 3
        else:
            evening_shift = 3
    if counter2 > 7:
        counter2 = 1
    elif counter2 > 5:
        if morning_shift == 2:
            morning_shift = 3
        else:
            evening_shift = 3
    
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
        cursor.execute("""INSERT INTO Orders (OrderTime) VALUES (?)""", (date,))
    date = date.replace(hour=0, minute=0, second=0)
    date += timedelta(days=1)
cursor.execute("""SELECT DISTINCT OrderTime FROM Orders ORDER BY OrderTime""")
sorted_data = [row[0] for row in cursor.fetchall()]
cursor.execute("""DELETE FROM Orders""")
for row in sorted_data:
    cursor.execute("""INSERT INTO Orders (OrderTime) VALUES (?)""", (row,))

# creates array with order IDs
cursor.execute("""SELECT OrderID FROM Orders""")
order_id = [row[0] for row in cursor.fetchall()]

# inserts order types
for row in order_id:
    cursor.execute("""UPDATE Orders SET OrderTypeID = ? WHERE OrderID = ?""", (random.randint(1, 4), row))

# inserts payment types and if a filled out stamp card is presented
for row in order_id:
    cursor.execute("""SELECT OrderTypeID FROM Orders WHERE OrderID = ?""", (row,))
# checking which payment types are possible for order type
    if cursor.fetchone()[0] in [1, 3]:
        cursor.execute("""UPDATE Orders SET PaymentTypeID = ? WHERE OrderID = ?""", (random.randint(1, 3), row))
        cursor.execute("""UPDATE Orders SET StampCouponAmount = ? WHERE OrderID = ?""", (random.choice([None, 1]), row))
    else:
        cursor.execute("""UPDATE Orders SET PaymentTypeID = ? WHERE OrderID = ?""", (random.randint(1, 2), row))

# inserts which cashiers served the order
prevdate = datetime.min
set_shifts()
for row in order_id:
    cursor.execute("""SELECT OrderTime FROM Orders WHERE OrderID = ?""", (row,))
    date = datetime.strptime(cursor.fetchone()[0], '%Y-%m-%d %H:%M:%S')
# checks if order is in the same day as the previous order
    if date.day != prevdate.day and prevdate.day != datetime.min:
        counter1 +=1
        counter2 +=1
        set_shifts()
# checks in which shift the order is placed
    if date.hour < 19:
        cashier = morning_shift
    else:
        cashier = evening_shift
    cursor.execute("""UPDATE Orders SET CashierID = ? WHERE OrderID = ?""", (cashier, row))
    prevdate = date

conn.commit()




               