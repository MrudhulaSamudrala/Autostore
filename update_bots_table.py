#!/usr/bin/env python3
"""
Script to add carried_bin_id column to bots table
"""

import sqlite3
import os

def update_bots_table():
    """Add carried_bin_id column to bots table"""
    
    # Connect to the database
    db_path = "autostore.db"
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(bots)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'carried_bin_id' not in columns:
            print("Adding carried_bin_id column to bots table...")
            cursor.execute("ALTER TABLE bots ADD COLUMN carried_bin_id INTEGER REFERENCES bins(id)")
            conn.commit()
            print("✅ Successfully added carried_bin_id column to bots table")
        else:
            print("✅ carried_bin_id column already exists in bots table")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(bots)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Current bots table columns: {columns}")
        
    except Exception as e:
        print(f"❌ Error updating bots table: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_bots_table() 