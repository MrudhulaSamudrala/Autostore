import sqlite3

def print_bin_locks_schema():
    conn = sqlite3.connect('autostore.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(bin_locks);")
    columns = cursor.fetchall()
    print("bin_locks table schema:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    conn.close()

if __name__ == "__main__":
    print_bin_locks_schema() 