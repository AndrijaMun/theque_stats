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
        payment_type = random.randint(1, 3)
        cursor.execute("""UPDATE Orders SET PaymentTypeID = ? WHERE OrderID = ?""", (payment_type, row))
# checking if stampcard usage is possible for payment type
        if payment_type != 3:
            cursor.execute("""UPDATE Orders SET StampCouponAmount = ? WHERE OrderID = ?""", (random.choice([None, 1]), row))
    else:
        payment_type = random.randint(1, 2)
        cursor.execute("""UPDATE Orders SET PaymentTypeID = ? WHERE OrderID = ?""", (payment_type, row))

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

# inserts items for each order
cursor.execute("""SELECT MAX(ItemID) From Items""")
total_items = cursor.fetchone()[0]
for row in order_id:
    item_list = list(range(1, total_items + 1))
    for _ in range (1, random.randint(2, 6)):
        item = random.choice(item_list)
        item_list.remove(item)
        item_amount = random.randint(1, 3)
        cursor.execute("""SELECT ItemPrice FROM Items WHERE ItemID = ?""", (item,))
        item_price = cursor.fetchone()[0]
        cursor.execute("""INSERT INTO OrderItems (ItemID, ItemAmount, PriceTotal, OrderID) VALUES (?, ?, ?, ?)""", (item, item_amount, item_amount * item_price, row))

# inserts addons for each item
cursor.execute("""SELECT MAX(AddOnID) From AddOns""")
total_addons = cursor.fetchone()[0]
cursor.execute("""SELECT OrderItemID FROM OrderItems""")
orderitems_id = [row[0] for row in cursor.fetchall()]
for row in orderitems_id:
    addon_list = list(range(1, total_addons + 1))
    for _ in range (1, random.randint(2, 3)):
        addon = random.choice(addon_list)
        addon_list.remove(addon)
        addon_amount = random.randint(1, 2)
        cursor.execute("""SELECT AddOnPrice FROM AddOns WHERE AddOnID = ?""", (addon,))
        addon_price = cursor.fetchone()[0]
        cursor.execute("""INSERT INTO ItemAddOns (AddOnID, AddOnAmount, PriceTotal, OrderItemID) VALUES (?, ?, ?, ?)""", (addon, addon_amount, addon_amount * addon_price, row))

# inserts total order amount
for row in order_id:
    cursor.execute("""SELECT PaymentTypeID FROM Orders WHERE OrderID = ?""", (row,))
    free_check = cursor.fetchone()[0]
    if free_check == 3:
        cursor.execute("""UPDATE Orders SET OrderAmount = 0 WHERE OrderID = ?""", (row,))
    else:
        cursor.execute("""SELECT SUM(PriceTotal) FROM OrderItems WHERE OrderID = ?""", (row,))
        item_total = cursor.fetchone()[0] or 0 
        cursor.execute("""SELECT SUM(PriceTotal) FROM ItemAddOns WHERE OrderItemID IN (SELECT OrderItemID FROM OrderItems WHERE OrderID = ?)""", (row,))
        addon_total = cursor.fetchone()[0] or 0 
        cursor.execute("""UPDATE Orders SET OrderAmount = ? WHERE OrderID = ?""", (item_total + addon_total, row))
    
conn.commit()
conn.close()



               