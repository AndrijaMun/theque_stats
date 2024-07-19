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
popular_addons = popular_addons.merge(addons[['AddOnID', 'AddOn']], on='AddOnID').sort_values(by='AddOnAmount', ascending=False)

# Most popular item and add-on combination
item_addon_combo = item_addons.groupby(['OrderItemID', 'AddOnID'])['AddOnAmount'].sum().reset_index()
item_addon_combo = item_addon_combo.merge(order_items, on='OrderItemID')
item_addon_combo = item_addon_combo.merge(items[['ItemID', 'ItemName']], on='ItemID')
item_addon_combo = item_addon_combo.merge(addons[['AddOnID', 'AddOn']], on='AddOnID')
item_addon_combo = item_addon_combo.groupby(['ItemName', 'AddOn'])['AddOnAmount'].sum().reset_index().sort_values(by='AddOnAmount', ascending=False)

# Most popular flavors
popular_flavors = order_items.merge(items[['ItemID', 'ItemFlavour']], on='ItemID')
popular_flavors = popular_flavors.groupby('ItemFlavour')['ItemID'].count().reset_index().rename(columns={'ItemID': 'ItemCount'}).sort_values(by='ItemCount', ascending=False)

# Busiest hours on average
orders['OrderHour'] = pd.to_datetime(orders['OrderTime']).dt.hour
busiest_hours = orders.groupby('OrderHour')['OrderID'].count().reset_index().rename(columns={'OrderID': 'OrderCount'}).sort_values(by='OrderCount', ascending=False)

# Busiest days of the week on average
orders['OrderDate'] = pd.to_datetime(orders['OrderTime']).dt.date
orders['OrderDay'] = pd.to_datetime(orders['OrderDate']).dt.dayofweek
busiest_days = orders.groupby('OrderDay')['OrderID'].count().reset_index().rename(columns={'OrderID': 'OrderCount'}).sort_values(by='OrderCount', ascending=False)

# Actual busiest day in the given time period
busiest_actual_day = orders.groupby('OrderDate')['OrderID'].count().reset_index().rename(columns={'OrderID': 'OrderCount'}).sort_values(by='OrderCount', ascending=False).iloc[0]

# Cashier that sold most items
cashier_sales = order_items.merge(orders, on='OrderID').groupby('CashierID')['ItemAmount'].sum().reset_index().merge(cashiers, on='CashierID').sort_values(by='ItemAmount', ascending=False)

# Cashier that generated the most traffic
cashier_traffic = orders.groupby('CashierID')['OrderID'].count().reset_index().rename(columns={'OrderID': 'OrderCount'}).merge(cashiers, on='CashierID').sort_values(by='OrderCount', ascending=False)

# Cashier that generated the most revenue
cashier_revenue = orders.groupby('CashierID')['OrderAmount'].sum().reset_index().merge(cashiers, on='CashierID').sort_values(by='OrderAmount', ascending=False)

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
            column_letter = chr(65 + c_idx - 1)
            sheet.column_dimensions[column_letter].width = max(sheet.column_dimensions[column_letter].width, len(str(value)) + 2)

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

# Create a new sheet for most popular flavors
ws_popular_flavors = wb.create_sheet("Popular Flavors")
write_df_to_sheet(popular_flavors, ws_popular_flavors)

# Create a new sheet for busiest times
ws_busiest_times = wb.create_sheet("Busiest Times")
write_df_to_sheet(busiest_hours, ws_busiest_times, start_row=1)
write_df_to_sheet(busiest_days, ws_busiest_times, start_row=len(busiest_hours) + 3)
write_df_to_sheet(pd.DataFrame([busiest_actual_day]), ws_busiest_times, start_row=len(busiest_hours) + len(busiest_days) + 5)

# Create a new sheet for cashier sales, traffic, and revenue
ws_cashier = wb.create_sheet("Cashier Performance")
write_df_to_sheet(cashier_sales, ws_cashier, start_row=1)
write_df_to_sheet(cashier_traffic, ws_cashier, start_row=len(cashier_sales) + 3)
write_df_to_sheet(cashier_revenue, ws_cashier, start_row=len(cashier_sales) + len(cashier_traffic) + 6)

# Generate a chart for sales by payment type
plt.figure(figsize=(10, 6))
plt.bar(sales_by_payment_type['PaymentType'], sales_by_payment_type['OrderAmount'])
plt.title('Sales by Payment Type')
plt.xlabel('Payment Type')
plt.ylabel('Sales')
plt.xticks(rotation=45)
plt.savefig('sales_by_payment_type.png')

# Insert the chart into the sheet
img = Image('sales_by_payment_type.png')
ws.add_image(img, 'E1')

# Generate a chart for sales by order type
plt.figure(figsize=(10, 6))
plt.bar(sales_by_order_type['OrderType'], sales_by_order_type['OrderAmount'])
plt.title('Sales by Order Type')
plt.xlabel('Order Type')
plt.ylabel('Sales')
plt.xticks(rotation=45)
plt.savefig('sales_by_order_type.png')

# Insert the chart into the order type sheet
img = Image('sales_by_order_type.png')
ws_order_type.add_image(img, 'E1')

# Generate a chart for popular items
plt.figure(figsize=(10, 6))
plt.barh(popular_items['ItemName'], popular_items['ItemAmount'])
plt.title('Most Popular Items')
plt.xlabel('Sales')
plt.ylabel('Item')
plt.tight_layout()
plt.savefig('popular_items.png')

# Insert the chart into the popular items sheet
img = Image('popular_items.png')
ws_popular_items.add_image(img, 'E1')

# Generate a chart for popular addons
plt.figure(figsize=(10, 6))
plt.barh(popular_addons['AddOn'], popular_addons['AddOnAmount'])
plt.title('Most Popular AddOns')
plt.xlabel('Sales')
plt.ylabel('AddOn')
plt.tight_layout()
plt.savefig('popular_addons.png')

# Insert the chart into the popular addons sheet
img = Image('popular_addons.png')
ws_popular_addons.add_image(img, 'E1')

# Generate a chart for popular flavors
plt.figure(figsize=(10, 6))
plt.barh(popular_flavors['ItemFlavour'], popular_flavors['ItemCount'])
plt.title('Most Popular Flavors')
plt.xlabel('Count')
plt.ylabel('Flavor')
plt.tight_layout()
plt.savefig('popular_flavors.png')

# Insert the chart into the popular flavors sheet
img = Image('popular_flavors.png')
ws_popular_flavors.add_image(img, 'E1')

# Generate a chart for busiest hours
plt.figure(figsize=(10, 6))
plt.plot(busiest_hours['OrderHour'], busiest_hours['OrderCount'])
plt.title('Busiest Hours')
plt.xlabel('Hour')
plt.ylabel('Order Count')
plt.grid(True)
plt.tight_layout()
plt.savefig('busiest_hours.png')

# Insert the chart into the busiest times sheet
img = Image('busiest_hours.png')
ws_busiest_times.add_image(img, 'E1')

# Generate a chart for busiest days
plt.figure(figsize=(10, 6))
plt.plot(busiest_days['OrderDay'], busiest_days['OrderCount'])
plt.title('Busiest Days')
plt.xlabel('Day of the Week')
plt.ylabel('Order Count')
plt.grid(True)
plt.tight_layout()
plt.savefig('busiest_days.png')

# Insert the chart into the busiest times sheet
img = Image('busiest_days.png')
ws_busiest_times.add_image(img, f'E{len(busiest_hours) + 4}')

# Generate a chart for cashier sales
plt.figure(figsize=(10, 6))
plt.barh(cashier_sales['CashierName'], cashier_sales['ItemAmount'])
plt.title('Cashier Sales')
plt.xlabel('Items Sold')
plt.ylabel('Cashier')
plt.tight_layout()
plt.savefig('cashier_sales.png')

# Insert the chart into the cashier sheet
img = Image('cashier_sales.png')
ws_cashier.add_image(img, 'E1')

# Generate a chart for cashier traffic
plt.figure(figsize=(10, 6))
plt.barh(cashier_traffic['CashierName'], cashier_traffic['OrderCount'])
plt.title('Cashier Traffic')
plt.xlabel('Order Count')
plt.ylabel('Cashier')
plt.tight_layout()
plt.savefig('cashier_traffic.png')

# Insert the chart into the cashier sheet
img = Image('cashier_traffic.png')
ws_cashier.add_image(img, f'E{len(cashier_sales) + 4}')

# Generate a chart for cashier revenue
plt.figure(figsize=(10, 6))
plt.barh(cashier_revenue['CashierName'], cashier_revenue['OrderAmount'])
plt.title('Cashier Revenue')
plt.xlabel('Revenue')
plt.ylabel('Cashier')
plt.tight_layout()
plt.savefig('cashier_revenue.png')

# Insert the chart into the cashier sheet
img = Image('cashier_revenue.png')
ws_cashier.add_image(img, f'E{len(cashier_sales) + len(cashier_traffic) + 7}')

# Save the workbook
wb.save('analyzed_data.xlsx')
