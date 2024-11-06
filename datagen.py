import os
import sqlite3
import random
import subprocess

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
sorted_dt = [dt[0] for dt in cursor.fetchall()]
cursor.execute("""DELETE FROM Orders""")
cursor.execute("""DELETE FROM sqlite_sequence WHERE name='Orders'""")
for dt in sorted_dt:
    cursor.execute("""INSERT INTO Orders (OrderTime) VALUES (?)""", (dt,))

# creates array with order IDs
cursor.execute("""SELECT OrderID FROM Orders""")
order_id = [id[0] for id in cursor.fetchall()]

# inserts order types
for id in order_id:
    cursor.execute("""UPDATE Orders SET OrderTypeID = ? WHERE OrderID = ?""", (random.randint(1, 4), id))

# inserts payment types and if a filled out stamp card is presented
for id in order_id:
    cursor.execute("""SELECT OrderTypeID FROM Orders WHERE OrderID = ?""", (id,))
# checking which payment types are possible for order type
    if cursor.fetchone()[0] in [1, 3]:
        payment_type = random.randint(1, 3)
        cursor.execute("""UPDATE Orders SET PaymentTypeID = ? WHERE OrderID = ?""", (payment_type, id))
# checking if stampcard usage is possible for payment type
        if payment_type != 3:
            cursor.execute("""UPDATE Orders SET StampCouponAmount = ? WHERE OrderID = ?""", (random.choice([None, 1]), id))
    else:
        payment_type = random.randint(1, 2)
        cursor.execute("""UPDATE Orders SET PaymentTypeID = ? WHERE OrderID = ?""", (payment_type, id))

# inserts which cashiers served the order
prevdate = datetime.min
set_shifts()
for id in order_id:
    cursor.execute("""SELECT OrderTime FROM Orders WHERE OrderID = ?""", (id,))
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
    cursor.execute("""UPDATE Orders SET CashierID = ? WHERE OrderID = ?""", (cashier, id))
    prevdate = date

# inserts items for each order
cursor.execute("""SELECT MAX(ItemID) From Items""")
total_items = cursor.fetchone()[0]
for id in order_id:
    item_list = list(range(1, total_items + 1))
    cursor.execute("""SELECT OrderTypeID FROM Orders WHERE OrderID == ?""", (id,))
    ordertype_id = cursor.fetchone()[0]
    if ordertype_id == 4:
        cursor.execute("""SELECT ItemID FROM Items WHERE ItemTypeID IN (1, 2, 3)""")
        item_icecream = [item[0] for item in cursor.fetchall()]
        item_list = [item for item in item_list if item not in item_icecream]
    for _ in range (1, random.randint(2, 6)):
        item = random.choice(item_list)
        item_list.remove(item)
        item_amount = random.randint(1, 3)
        cursor.execute("""SELECT ItemPrice FROM Items WHERE ItemID = ?""", (item,))
        item_price = cursor.fetchone()[0]
        cursor.execute("""INSERT INTO OrderItems (ItemID, ItemAmount, PriceTotal, OrderID) VALUES (?, ?, ?, ?)""", (item, item_amount, item_amount * item_price, id))

# inserts addons for each item
cursor.execute("""SELECT MAX(AddOnID) From AddOns""")
total_addons = cursor.fetchone()[0]
cursor.execute("""SELECT OrderItems.OrderItemID, Items.ItemTypeID FROM OrderItems JOIN Items ON OrderItems.ItemID = Items.ItemID""")
orderitems_data = cursor.fetchall()
for orderitem_id, itemtype_id in orderitems_data:
    addon_list = list(range(1, total_addons + 1))
# checks if item can have add-ons
    if itemtype_id != 6:
        if itemtype_id != 1:
            addon_list.remove(23)
        for _ in range (1, random.randint(2, 3)):
            addon = random.choice(addon_list)
            addon_list.remove(addon)
            if addon == 23:
                addon_amount = 1
            else:
                addon_amount = random.randint(1, 2)
            cursor.execute("""SELECT AddOnPrice FROM AddOns WHERE AddOnID = ?""", (addon,))
            addon_price = cursor.fetchone()[0]
            cursor.execute("""INSERT INTO ItemAddOns (AddOnID, AddOnAmount, PriceTotal, OrderItemID) VALUES (?, ?, ?, ?)""", (addon, addon_amount, addon_amount * addon_price, orderitem_id))

# inserts total order amount
cursor.execute("""
    SELECT Orders.OrderID, 
           Orders.PaymentTypeID, 
           Orders.StampCouponAmount,
           COALESCE(SUM(OrderItems.PriceTotal), 0) AS ItemTotal, 
           COALESCE(SUM(ItemAddOns.PriceTotal), 0) AS AddOnTotal,
           MAX(Items.ItemPrice) AS MaxItemPrice,
           MAX(AddOns.AddOnPrice) AS MaxAddonPrice
    FROM Orders
    LEFT JOIN OrderItems ON Orders.OrderID = OrderItems.OrderID
    LEFT JOIN Items ON OrderItems.ItemID = Items.ItemID
    LEFT JOIN ItemAddOns ON OrderItems.OrderItemID = ItemAddOns.OrderItemID
    LEFT JOIN AddOns ON ItemAddOns.AddOnID = AddOns.AddOnID
    GROUP BY Orders.OrderID
""")
order_total = cursor.fetchall()
for order_id, payment_type, stamp_check, item_total, addon_total, max_item_price, max_addon_price in order_total:
# adds up total item prices and total add-on prices
    order_total = item_total + addon_total
# checks if payment type is via coupon
    if payment_type == 3:
        order_total = 0
    else:
# reduces price if stamp card is presented
        if stamp_check == 1:
            order_total -= (max_item_price or 0) + (max_addon_price or 0)
    cursor.execute("""UPDATE Orders SET OrderAmount = ? WHERE OrderID = ?""", (order_total, order_id))


conn.commit()
conn.close()

script_name = 'dataproc.py'
script_path = os.path.join(os.path.dirname(__file__), script_name)

try:
    subprocess.run(['python', script_path], check=True)
except subprocess.CalledProcessError as e:
    print(f"Error occurred while running {script_name}: {e}")

               