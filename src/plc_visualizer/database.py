from pathlib import Path
import aiosqlite
from datetime import datetime

DB_PATH = Path(__file__).parent / "data" / "plc_data.db"

async def init_db():
    """Initialize the database and create tables if they don't exist"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS plc_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_name TEXT NOT NULL,
                value REAL NOT NULL,
                timestamp DATETIME NOT NULL
            )
        ''')
        
        await db.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON plc_readings(timestamp)')
        await db.execute('CREATE INDEX IF NOT EXISTS idx_tag_name ON plc_readings(tag_name)')
        
        await db.commit()

async def save_reading(tag_name, value, timestamp=None):
    """Save a PLC tag reading to the database"""
    if timestamp is None:
        timestamp = datetime.now()
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'INSERT INTO plc_readings (tag_name, value, timestamp) VALUES (?, ?, ?)',
            (tag_name, value, timestamp)
        )
        await db.commit()

async def get_historical_data(tag_name, start_time, end_time):
    """Get historical data for a specific tag within a time range"""
    print(f"Querying database for tag {tag_name} from {start_time} to {end_time}")
    
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        # First, let's check what data we actually have
        cursor = await db.execute(
            '''SELECT MIN(timestamp) as min_time, MAX(timestamp) as max_time, COUNT(*) as count
               FROM plc_readings 
               WHERE tag_name = ?''',
            (tag_name,)
        )
        range_info = await cursor.fetchone()
        print(f"Database info for {tag_name}:")
        print(f"  - Total records: {range_info['count']}")
        print(f"  - Date range: {range_info['min_time']} to {range_info['max_time']}")
        
        cursor = await db.execute(
            '''SELECT timestamp, value
               FROM plc_readings
               WHERE tag_name = ? 
               AND datetime(timestamp) BETWEEN datetime(?) AND datetime(?)
               ORDER BY timestamp''',
            (tag_name, start_time, end_time)
        )
        data = await cursor.fetchall()
        print(f"Found {len(data)} records in requested time range")
        return data
