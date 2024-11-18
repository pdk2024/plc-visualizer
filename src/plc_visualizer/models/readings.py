from sqlalchemy import Column, Integer, Float, DateTime, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PLCReading(Base):
    __tablename__ = 'plc_readings'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    tag_name = Column(String, nullable=False)
    value = Column(Float)

    def __repr__(self):
        return f"<PLCReading(timestamp={self.timestamp}, tag={self.tag_name}, value={self.value})>"
