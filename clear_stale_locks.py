#!/usr/bin/env python3
"""
Clear stale bin locks that are preventing order assignment.
"""

import sys
import os
from sqlalchemy import text

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.database import SessionLocal

def clear_stale_locks():
    """Clear bin locks that are not being used by active bots."""
    db = SessionLocal()
    try:
        # Get all bin locks
        cursor = db.execute(text("""
            SELECT id, used_by, status 
            FROM bin_locks 
            ORDER BY id
        """))
        locks = cursor.fetchall()
        print("🔒 Current Bin Locks:")
        for lock in locks:
            print(f"   Bin {lock[0]}: Used by Bot {lock[1]}, Status={lock[2]}")
        # Get all bots and their current status
        cursor = db.execute(text("""
            SELECT id, status, current_order_id, carried_bin_id
            FROM bots 
            ORDER BY id
        """))
        bots = cursor.fetchall()
        print("\n🤖 Current Bot Status:")
        for bot in bots:
            print(f"   Bot {bot[0]}: Status={bot[1]}, Order={bot[2]}, Carried={bot[3]}")
        # Find stale locks (locks held by idle bots or bots not processing orders)
        stale_locks = []
        for lock in locks:
            bin_id, used_by, status = lock
            # Find the bot that holds this lock
            bot_info = next((bot for bot in bots if bot[0] == used_by), None)
            if bot_info:
                bot_id, bot_status, order_id, carried_bin = bot_info
                # Check if this is a stale lock
                is_stale = (
                    bot_status == 'idle' or  # Bot is idle
                    order_id is None or      # Bot has no order
                    (bot_status == 'idle' and carried_bin is None)  # Bot is idle and not carrying anything
                )
                if is_stale:
                    stale_locks.append(bin_id)
                    print(f"   ❌ Bin {bin_id} lock is stale (held by idle Bot {used_by})")
                else:
                    print(f"   ✅ Bin {bin_id} lock is active (held by Bot {used_by} with order {order_id})")
        if not stale_locks:
            print("\n✅ No stale locks found!")
            return
        print(f"\n🧹 Clearing {len(stale_locks)} stale locks...")
        # Clear stale locks
        for bin_id in stale_locks:
            db.execute(text("DELETE FROM bin_locks WHERE id = :bin_id"), {"bin_id": bin_id})
            print(f"   🗑️  Cleared lock for Bin {bin_id}")
        db.commit()
        print(f"\n✅ Successfully cleared {len(stale_locks)} stale locks!")
        # Verify locks are cleared
        cursor = db.execute(text("SELECT COUNT(*) FROM bin_locks"))
        remaining_locks = cursor.fetchone()[0]
        print(f"📊 Remaining locks: {remaining_locks}")
    except Exception as e:
        print(f"❌ Error clearing locks: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🧹 Clearing Stale Bin Locks")
    print("=" * 50)
    clear_stale_locks() 