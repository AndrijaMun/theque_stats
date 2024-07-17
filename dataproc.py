import sqlite3
import pandas as pd
import numpy as np
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.drawing.image import Image
from openpyxl.styles import Alignment
import matplotlib.pyplot as plt

# Connect to the SQLite database
conn = sqlite3.connect('theque.db')

# Retrieve data from the tables
orders = pd.read_sql_query("SELECT * FROM Orders", conn)
order_items = pd.read_sql_query("SELECT * FROM OrderItems", conn)
items = pd.read_sql_query("SELECT * FROM Items", conn)
cashiers = pd.read_sql_query("SELECT * FROM Cashiers", conn)
order_types = pd.read_sql_query("SELECT * FROM OrderTypes", conn)
payment_types = pd.read_sql_query("SELECT * FROM PaymentTypes", conn)
addons = pd.read_sql_query("SELECT * FROM AddOns", conn)
item_addons = pd.read_sql_query("SELECT * FROM ItemAddOns", conn)
item_flavours = pd.read_sql_query("SELECT * FROM ItemFlavours", conn)

conn.close()

# Add item flavours to Items dataframe
items = items.merge(item_flavours, left_on='ItemFlavourID', right_on='ItemFlavourID', how='left')
items['ItemName'] = items.apply(lambda x: f"{x['ItemName']} ({x['ItemFlavour']})" if pd.notna(x['ItemFlavour']) else x['ItemName'], axis=1)

# Total sales
total_sales = orders['OrderAmount'].sum()

# Number of orders
total_orders = orders['OrderID'].nunique()

# Sales by payment type
sales_by_payment_type = orders.groupby('PaymentTypeID')['OrderAmount'].sum().reset_index()
sales_by_payment_type = sales_by_payment_type.merge(payment_types, on='PaymentTypeID')

# Sales by order type
sales_by_order_type = orders.groupby('OrderTypeID')['OrderAmount'].sum().reset_index()
sales_by_order_type = sales_by_order_type.merge(order_types, on='OrderTypeID')

# Most popular items
popular_items = order_items.groupby('ItemID')['ItemAmount'].sum().reset_index()
popular_items = popular_items.merge(items[['ItemID', 'ItemName']], on='ItemID').sort_values(by='ItemAmount', ascending=False)

# Most popular addons
popular_addons = item_addons.groupby('AddOnID')['AddOnAmount'].sum().reset_index()
popular_addons = popular_addons.merge(addons[['AddOnID', 'AddOn']], on='AddOnID').sort_values(by= 'AddOnAmount', ascending=False)

# Most popular item and add-on combination
item_addon_combo = item_addons.groupby(['OrderItemID', 'AddOnID'])['AddOnAmount'].sum().reset_index()
item_addon_combo = item_addon_combo.merge(order_items, on='OrderItemID')
item_addon_combo = item_addon_combo.merge(items[['ItemID', 'ItemName']], on='ItemID')
item_addon_combo = item_addon_combo.merge(addons[['AddOnID', 'AddOn']], on='AddOnID')
item_addon_combo = item_addon_combo.groupby(['ItemName', 'AddOn'])['AddOnAmount'].sum().reset_index().sort_values(by='AddOnAmount', ascending=False)

# Most popular flavor across all product types
popular_flavor_overall = items.groupby('ItemFlavour')['ItemID'].count().reset_index().rename(columns={'ItemID': 'ItemCount'}).sort_values(by= 'ItemCount', ascending=False).iloc[0]

# Busiest hours on average
orders['OrderHour'] = pd.to_datetime(orders['OrderTime']).dt.hour
busiest_hours = orders.groupby('OrderHour')['OrderID'].count().reset_index().rename(columns={'OrderID': 'OrderCount'}).sort_values(by='OrderCount', ascending=False)

# Busiest days of the week on average
orders['OrderDay'] = pd.to_datetime(orders['OrderTime']).dt.dayofweek
busiest_days = orders.groupby('OrderDay')['OrderID'].count().reset_index().rename(columns={'OrderID': 'OrderCount'}).sort_values(by='OrderCount', ascending=False)

# Actual busiest day in the given time period
orders['OrderDate'] = pd.to_datetime(orders['OrderTime']).dt.date
busiest_actual_day = orders.groupby('OrderDate')['OrderID'].count().reset_index().rename(columns={'OrderID': 'OrderCount'}).sort_values(by='OrderCount', ascending=False).iloc[0]

# Cashier that sold most items
cashier_sales = order_items.merge(orders, on='OrderID').groupby('CashierID')['ItemAmount'].sum().reset_index().merge(cashiers, on='CashierID').sort_values(by='ItemAmount', ascending=False)

# Cashier that generated the most traffic
cashier_traffic = orders.groupby('CashierID')['OrderID'].count().reset_index().rename(columns={'OrderID': 'OrderCount'}).merge(cashiers, on='CashierID').sort_values(by='OrderCount', ascending=False)

# Create a workbook and select the active worksheet
wb = Workbook()
ws = wb.active

# Function to write a DataFrame to Excel sheet and adjust column widths
def write_df_to_sheet(df, sheet, start_row=1, start_col=1):
    for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), start_row):
        for c_idx, value in enumerate(row, start_col):
            cell = sheet.cell(row=r_idx, column=c_idx, value=value)
            cell.alignment = Alignment(wrap_text=True)  # Enable text wrapping
            # Adjust column width based on content length
            sheet.column_dimensions[chr(65 + c_idx - 1)].width = max(sheet.column_dimensions[chr(65 + c_idx - 1)].width, len(str(value)) + 2)

# Write total sales and number of orders
ws['A1'] = 'Total Sales'
ws['B1'] = total_sales
ws['A2'] = 'Total Orders'
ws['B2'] = total_orders

# Write sales by payment type
ws.title = "Sales by Payment Type"
write_df_to_sheet(sales_by_payment_type, ws, start_row=4)

# Create a new sheet for sales by order type
ws_order_type = wb.create_sheet("Sales by Order Type")
write_df_to_sheet(sales_by_order_type, ws_order_type)

# Create a new sheet for popular items
ws_popular_items = wb.create_sheet("Popular Items")
write_df_to_sheet(popular_items[['ItemName', 'ItemAmount']], ws_popular_items)

# Create a new sheet for popular addons
ws_popular_addons = wb.create_sheet("Popular AddOns")
write_df_to_sheet(popular_addons[['AddOn', 'AddOnAmount']], ws_popular_addons)

# Create a new sheet for most popular item and add-on combination
ws_item_addon_combo = wb.create_sheet("Item-AddOn Combos")
write_df_to_sheet(item_addon_combo[['ItemName', 'AddOn', 'AddOnAmount']], ws_item_addon_combo)

# Create a new sheet for most popular flavor across all product types
ws_popular_flavor = wb.create_sheet("Popular Flavor Overall")
write_df_to_sheet(pd.DataFrame([popular_flavor_overall]), ws_popular_flavor)

# Create a new sheet for busiest hours
ws_busiest_hours = wb.create_sheet("Busiest Hours")
write_df_to_sheet(busiest_hours, ws_busiest_hours)

# Create a new sheet for busiest days of the week
ws_busiest_days = wb.create_sheet("Busiest Days")
write_df_to_sheet(busiest_days, ws_busiest_days)

# Create a new sheet for actual busiest day
ws_busiest_actual_day = wb.create_sheet("Busiest Actual Day")
write_df_to_sheet(pd.DataFrame([busiest_actual_day]), ws_busiest_actual_day)

# Create a new sheet for cashier sales
ws_cashier_sales = wb.create_sheet("Cashier Sales")
write_df_to_sheet(cashier_sales, ws_cashier_sales)

# Create a new sheet for cashier traffic
ws_cashier_traffic = wb.create_sheet("Cashier Traffic")
write_df_to_sheet(cashier_traffic, ws_cashier_traffic)

# Generate a chart for sales by payment type
plt.figure(figsize=(10, 6))
plt.bar(sales_by_payment_type['PaymentType'], sales_by_payment_type['OrderAmount'])
plt.title('Sales by Payment Type')
plt.xlabel('Payment Type')
plt.ylabel('Sales')
plt.savefig('sales_by_payment_type.png')

# Insert the chart into the sheet
img = Image('sales_by_payment_type.png')
ws.add_image(img, 'E1')

# Save the workbook
wb.save('analyzed_data.xlsx')
