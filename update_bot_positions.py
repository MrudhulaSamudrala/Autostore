#!/usr/bin/env python3
"""
Update bot positions in SQLite database.
Bot 1: (x=5, y=0, z=5)
Bot 2: (x=5, y=0, z=4)
"""

import sqlite3

def update_bot_positions():
    conn = sqlite3.connect("autostore.db")
    cursor = conn.cursor()
    
    # Update Bot 1
    cursor.execute("UPDATE bots SET x = ?, y = ?, current_location_z = ? WHERE id = ?", (5, 0, 5, 1))
    print("Bot 1 position set to (5,0,5)")
    
    # Update Bot 2
    cursor.execute("UPDATE bots SET x = ?, y = ?, current_location_z = ? WHERE id = ?", (5, 0, 4, 2))
    print("Bot 2 position set to (5,0,4)")
    
    conn.commit()
    conn.close()
    print("\n✅ Bot positions updated successfully.")

if __name__ == "__main__":
    update_bot_positions() 