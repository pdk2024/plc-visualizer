from pathlib import Path
import aiosqlite
from datetime import datetime

DB_PATH = Path(__file__).parent / "data" / "plc_data.db"

async def init_database():
    """Initialize the database and create tables if they don't exist"""
    # Ensure the data directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Create tables
        await db.execute('''
            CREATE TABLE IF NOT EXISTS plc_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_name TEXT NOT NULL,
                value REAL NOT NULL,
                timestamp DATETIME NOT NULL
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS tag_metadata (
                tag_name TEXT PRIMARY KEY,
                description TEXT
            )
        ''')
        
        await db.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON plc_readings(timestamp)')
        await db.execute('CREATE INDEX IF NOT EXISTS idx_tag_name ON plc_readings(tag_name)')
        
        await db.commit()
        
        # Check database status
        cursor = await db.execute("SELECT COUNT(*) as count FROM plc_readings")
        count = (await cursor.fetchone())[0]
        print(f"\nDatabase status:")
        print(f"Total records: {count}")
        
        if count > 0:
            cursor = await db.execute(
                "SELECT MIN(timestamp) as min_time, MAX(timestamp) as max_time FROM plc_readings"
            )
            range_data = await cursor.fetchone()
            print(f"Data range: {range_data[0]} to {range_data[1]}") 