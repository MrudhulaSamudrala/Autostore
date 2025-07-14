#!/usr/bin/env python3
"""
View Data from PostgreSQL Database
This script shows all your data in the PostgreSQL database.
"""

import psycopg2
from tabulate import tabulate

def view_database_data():
    """View all data in the PostgreSQL database"""
    
    try:
        # Connect to PostgreSQL database
        conn = psycopg2.connect('postgresql://postgres:post@localhost:5432/autostore')
        cursor = conn.cursor()
        
        print("🔍 Viewing data from PostgreSQL database...")
        print("=" * 60)
        
        # View products
        print("\n📦 PRODUCTS:")
        cursor.execute("SELECT id, name, price, quantity, category, bin_id FROM products LIMIT 10")
        products = cursor.fetchall()
        if products:
            headers = ["ID", "Name", "Price", "Quantity", "Category", "Bin ID"]
            print(tabulate(products, headers=headers, tablefmt="grid"))
            print(f"Total products: {len(products)} (showing first 10)")
        else:
            print("No products found")
        
        # View bins
        print("\n🗂️ BINS:")
        cursor.execute("SELECT id, x, y, z_location, status FROM bins LIMIT 10")
        bins = cursor.fetchall()
        if bins:
            headers = ["ID", "X", "Y", "Z", "Status"]
            print(tabulate(bins, headers=headers, tablefmt="grid"))
            print(f"Total bins: {len(bins)} (showing first 10)")
        else:
            print("No bins found")
        
        # View bots
        print("\n🤖 BOTS:")
        cursor.execute("SELECT id, name, status, current_x, current_y, current_z FROM bots")
        bots = cursor.fetchall()
        if bots:
            headers = ["ID", "Name", "Status", "X", "Y", "Z"]
            print(tabulate(bots, headers=headers, tablefmt="grid"))
        else:
            print("No bots found")
        
        # View orders
        print("\n📋 ORDERS:")
        cursor.execute("SELECT id, customer_name, status, total_amount FROM orders LIMIT 5")
        orders = cursor.fetchall()
        if orders:
            headers = ["ID", "Customer", "Status", "Total"]
            print(tabulate(orders, headers=headers, tablefmt="grid"))
            print(f"Total orders: {len(orders)} (showing first 5)")
        else:
            print("No orders found")
        
        # Count all records
        print("\n📊 DATABASE SUMMARY:")
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM bins")
        bin_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM bots")
        bot_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders")
        order_count = cursor.fetchone()[0]
        
        summary = [
            ["Products", product_count],
            ["Bins", bin_count],
            ["Bots", bot_count],
            ["Orders", order_count]
        ]
        print(tabulate(summary, headers=["Table", "Count"], tablefmt="grid"))
        
        conn.close()
        print("\n✅ Database connection successful!")
        print("🎉 Your data is safe and accessible!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    view_database_data() 