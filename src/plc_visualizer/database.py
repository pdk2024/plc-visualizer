from sqlalchemy import create_engine, Column, Integer, Float, DateTime, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import aiosqlite
import asyncio
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / 'plc_data.db'

# Define initial tag data
INITIAL_TAGS = [
    {
        'tag_name': 'CV31027_PIDE.SP',
        'description': 'Steam Pressure Setpoint',
        'units': 'bar',
        'min_value': 0,
        'max_value': 10
    },
    {
        'tag_name': 'CV31027_PIDE.PV',
        'description': 'Steam Pressure Process Variable',
        'units': 'bar',
        'min_value': 0,
        'max_value': 10
    },
    {
        'tag_name': 'CV31028_PIDE.SP',
        'description': 'Steam Temperature Setpoint',
        'units': '°C',
        'min_value': 0,
        'max_value': 200
    },
    {
        'tag_name': 'CV31028_PIDE.PV',
        'description': 'Steam Temperature Process Variable',
        'units': '°C',
        'min_value': 0,
        'max_value': 200
    },
    {
        'tag_name': 'CV31029_PIDE.SP',
        'description': 'Steam Flow Setpoint',
        'units': 'kg/h',
        'min_value': 0,
        'max_value': 1000
    },
    {
        'tag_name': 'CV31029_PIDE.PV',
        'description': 'Steam Flow Process Variable',
        'units': 'kg/h',
        'min_value': 0,
        'max_value': 1000
    }
]

Base = declarative_base()

class TagMetadata(Base):
    __tablename__ = 'tag_metadata'
    
    tag_name = Column(String, primary_key=True)
    description = Column(String, nullable=False)
    units = Column(String)
    min_value = Column(Float)
    max_value = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<TagMetadata(tag={self.tag_name}, description={self.description})>"

class PLCReading(Base):
    __tablename__ = 'plc_readings'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    tag_name = Column(String, ForeignKey('tag_metadata.tag_name'), nullable=False)
    value = Column(Float)

    # Relationship to tag metadata
    tag_info = relationship("TagMetadata")

    def __repr__(self):
        return f"<PLCReading(timestamp={self.timestamp}, tag={self.tag_name}, value={self.value})>"

async def init_db():
    """Initialize the database and create/update tag metadata"""
    print("Initializing database...")
    engine = create_engine(f'sqlite:///{DB_PATH}')
    Base.metadata.create_all(engine)
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Get existing tags
        cursor = await db.execute('SELECT tag_name FROM tag_metadata')
        existing_tags = {row[0] for row in await cursor.fetchall()}
        
        # Add or update tag metadata
        for tag in INITIAL_TAGS:
            if tag['tag_name'] in existing_tags:
                # Update existing tag
                await db.execute('''
                    UPDATE tag_metadata 
                    SET description = ?, units = ?, min_value = ?, max_value = ?
                    WHERE tag_name = ?
                ''', (
                    tag['description'],
                    tag['units'],
                    tag['min_value'],
                    tag['max_value'],
                    tag['tag_name']
                ))
            else:
                # Insert new tag
                await db.execute('''
                    INSERT INTO tag_metadata (tag_name, description, units, min_value, max_value)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    tag['tag_name'],
                    tag['description'],
                    tag['units'],
                    tag['min_value'],
                    tag['max_value']
                ))
        
        await db.commit()
        
        # Verify the metadata
        cursor = await db.execute('SELECT tag_name, description FROM tag_metadata')
        metadata = await cursor.fetchall()
        print(f"Current tag metadata ({len(metadata)} entries):")
        for tag in metadata:
            print(f"  - {tag[0]}: {tag[1]}")
    
    return engine

async def save_reading(timestamp, tag_name, value):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'INSERT INTO plc_readings (timestamp, tag_name, value) VALUES (?, ?, ?)',
            (timestamp, tag_name, value)
        )
        await db.commit()

async def get_historical_data(tag_name, start_time, end_time):
    """Get historical data for a specific tag within a time range"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            '''SELECT 
                r.timestamp, 
                r.value,
                m.description,
                m.units
               FROM plc_readings r
               JOIN tag_metadata m ON r.tag_name = m.tag_name
               WHERE r.tag_name = ? AND r.timestamp BETWEEN ? AND ?
               ORDER BY r.timestamp''',
            (tag_name, start_time, end_time)
        )
        return await cursor.fetchall()

async def get_tag_metadata(tag_name=None):
    """Get metadata for one or all tags"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if tag_name:
            cursor = await db.execute(
                'SELECT * FROM tag_metadata WHERE tag_name = ?',
                (tag_name,)
            )
            return await cursor.fetchone()
        else:
            cursor = await db.execute('SELECT * FROM tag_metadata')
            return await cursor.fetchall()

async def update_tag_metadata(tag_name, description=None, units=None, min_value=None, max_value=None):
    """Update metadata for a specific tag"""
    async with aiosqlite.connect(DB_PATH) as db:
        updates = []
        values = []
        if description is not None:
            updates.append('description = ?')
            values.append(description)
        if units is not None:
            updates.append('units = ?')
            values.append(units)
        if min_value is not None:
            updates.append('min_value = ?')
            values.append(min_value)
        if max_value is not None:
            updates.append('max_value = ?')
            values.append(max_value)
        
        if updates:
            updates.append('updated_at = ?')
            values.append(datetime.utcnow())
