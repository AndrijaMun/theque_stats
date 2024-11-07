import os
import sqlite3
import pandas as pd
import numpy as np
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.drawing.image import Image
from openpyxl.styles import Alignment
import matplotlib.pyplot as plt

# Create a new directory for the generated files
output_dir = 'analyzed_data_output'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

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

# Total sales and number of orders
total_sales = orders['OrderAmount'].sum()
total_orders = orders['OrderID'].nunique()

# Sales by payment type
sales_by_payment_type = orders.groupby('PaymentTypeID')['OrderAmount'].sum().reset_index()
sales_by_payment_type = sales_by_payment_type.merge(payment_types, on='PaymentTypeID')
sales_by_payment_type = sales_by_payment_type[sales_by_payment_type['PaymentType'] != 'Coupon']

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
item_addon_combo.rename(columns={'AddOnAmount': 'CombinationCount'}, inplace=True)

# Most popular flavors
popular_flavors = order_items.merge(items[['ItemID', 'ItemFlavour']], on='ItemID')
popular_flavors = popular_flavors.groupby('ItemFlavour')['ItemID'].count().reset_index().rename(columns={'ItemID': 'ItemCount'}).sort_values(by='ItemCount', ascending=False)

# Busiest hours and days
orders['OrderHour'] = pd.to_datetime(orders['OrderTime']).dt.hour
busiest_hours = orders.groupby('OrderHour')['OrderID'].count().reset_index().rename(columns={'OrderID': 'OrderCount'}).sort_values(by='OrderCount', ascending=False)
orders['OrderDate'] = pd.to_datetime(orders['OrderTime']).dt.date
orders['DayOfWeek'] = pd.to_datetime(orders['OrderDate']).dt.strftime('%A')
busiest_days = orders.groupby('DayOfWeek')['OrderID'].count().reset_index().rename(columns={'OrderID': 'OrderCount'}).sort_values(by='OrderCount', ascending=False)
busiest_actual_day = orders.groupby('OrderDate')['OrderID'].count().reset_index().rename(columns={'OrderID': 'OrderCount'}).sort_values(by='OrderCount', ascending=False)

# Cashier performance metrics
cashier_sales = order_items.merge(orders, on='OrderID').groupby('CashierID')['ItemAmount'].sum().reset_index().merge(cashiers, on='CashierID').sort_values(by='ItemAmount', ascending=False)
cashier_traffic = orders.groupby('CashierID')['OrderID'].count().reset_index().rename(columns={'OrderID': 'OrderCount'}).merge(cashiers, on='CashierID').sort_values(by='OrderCount', ascending=False)
cashier_revenue = orders.groupby('CashierID')['OrderAmount'].sum().reset_index().merge(cashiers, on='CashierID').sort_values(by='OrderAmount', ascending=False)

# Create a workbook and select the active worksheet
wb = Workbook()
ws = wb.active

# Function to write DataFrame to Excel with renaming and euro sign formatting
def write_df_to_sheet(df, sheet, start_row=1, start_col=1, rename_columns=None, format_columns=None):
    if rename_columns:
        df = df.rename(columns=rename_columns)
    
    if format_columns is None:
        format_columns = [col for col in df.columns if 'Amount' in col]
    
    euro_col_indices = [df.columns.get_loc(col) + start_col for col in format_columns if col in df.columns]
    
    for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), start_row):
        for c_idx, value in enumerate(row, start_col):
            cell = sheet.cell(row=r_idx, column=c_idx, value=value)
            cell.alignment = Alignment(wrap_text=True)
            
            if r_idx > start_row - 1 and c_idx in euro_col_indices:
                cell.number_format = u'€#,##0.00'
            
            column_letter = chr(65 + c_idx - 1)
            sheet.column_dimensions[column_letter].width = max(sheet.column_dimensions[column_letter].width, len(str(value)) + 2)

# Write summary data
ws['A1'] = 'Total Sales'
ws['B1'] = total_sales
ws['B1'].number_format = u'€#,##0.00'
ws['A2'] = 'Total Orders'
ws['B2'] = total_orders

# Rename the sheet to "Summary"
ws.title = "Summary"

# Write data to each sheet with specified renaming and euro formatting
ws_payment_type = wb.create_sheet("Sales by Payment Type")
write_df_to_sheet(sales_by_payment_type, ws_payment_type)

ws_order_type = wb.create_sheet("Sales by Order Type")
write_df_to_sheet(sales_by_order_type, ws_order_type)

write_df_to_sheet(
    popular_items[['ItemName', 'ItemAmount']], 
    wb.create_sheet("Popular Items"), 
    rename_columns={'ItemAmount': 'ItemCount'}
)

write_df_to_sheet(
    popular_addons[['AddOn', 'AddOnAmount']], 
    wb.create_sheet("Popular AddOns"), 
    rename_columns={'AddOnAmount': 'AddOnCount'}
)

write_df_to_sheet(
    popular_flavors, 
    wb.create_sheet("Popular Flavors"), 
    rename_columns={'ItemCount': 'FlavourCount'}
)

ws_busiest_times = wb.create_sheet("Busiest Times")
write_df_to_sheet(busiest_hours, ws_busiest_times, start_row=1)
write_df_to_sheet(busiest_days, ws_busiest_times, start_row=len(busiest_hours) + 3)
write_df_to_sheet(busiest_actual_day, ws_busiest_times, start_row=len(busiest_hours) + len(busiest_days) + 5)

ws_cashier = wb.create_sheet("Cashier Performance")
write_df_to_sheet(cashier_sales, ws_cashier, start_row=1)
write_df_to_sheet(cashier_traffic, ws_cashier, start_row=len(cashier_sales) + 3)
write_df_to_sheet(cashier_revenue, ws_cashier, start_row=len(cashier_sales) + len(cashier_traffic) + 6)

# Save the workbook
wb.save(f'{output_dir}/analyzed_data.xlsx')
