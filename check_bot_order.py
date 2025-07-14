from models.orders import Order
from models.bots import Bot
from db.database import SessionLocal

db = SessionLocal()
order = db.query(Order).filter(Order.id==42).first()
print('Order 42 assigned_bot_id:', order.assigned_bot_id)
if order and order.assigned_bot_id:
    bot = db.query(Bot).filter(Bot.id==order.assigned_bot_id).first()
    print(f'Bot {bot.id}: status={bot.status}, x={bot.x}, y={bot.y}, path={bot.path}, full_path={bot.full_path}')
db.close() 