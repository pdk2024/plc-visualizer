from quart import Quart, render_template, websocket, request
from pathlib import Path
import sys
import asyncio
from pycomm3 import LogixDriver
import json
from datetime import datetime, timedelta

from .database import (
    init_db, 
    save_reading, 
    get_historical_data
)

print("Starting application...")
print(f"Python version: {sys.version}")

app = Quart(__name__)

class PLCMonitor:
    def __init__(self, ip_address):
        self.ip_address = ip_address
        self.plc = None
        self.connected = False
        self.analog_tags = [
            'CV31027_PIDE.SP', 'CV31027_PIDE.PV',
            'CV31028_PIDE.SP', 'CV31028_PIDE.PV',
            'CV31029_PIDE.SP', 'CV31029_PIDE.PV',
            'CNVR31007_Limit_Infeed_Right_Analog',
            'CNVR31007_Limit_Infeed_Left_Analog',
            'CNVR31007_Limit_Outfeed_Right_Analog',
            'CNVR31007_Limit_Outfeed_Left_Analog',
            'PUMP31002_Running_Analog',
            'PUMP31004_Running_Analog'
        ]
        self.boolean_tags = [
            'CNVR31007_Limit_Infeed_Right',
            'CNVR31007_Limit_Infeed_Left',
            'CNVR31007_Limit_Outfeed_Right',
            'CNVR31007_Limit_Outfeed_Left'
        ]
        print(f"PLCMonitor initialized with IP: {ip_address}")

    async def connect(self):
        """Connect to the PLC"""
        try:
            print(f"Connecting to PLC at {self.ip_address}...")
            self.plc = LogixDriver(self.ip_address)
            self.plc.open()
            self.connected = True
            print("Successfully connected to PLC")
            
            # Test read to verify connection
            test_tag = self.analog_tags[0]
            test_read = self.plc.read(test_tag)
            print(f"Test read of {test_tag}: {test_read}")
            
            return True
            
        except Exception as e:
            print(f"Error connecting to PLC: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            self.connected = False
            if self.plc is not None:
                try:
                    self.plc.close()
                except:
                    pass
            self.plc = None
            return False

    async def read_data(self):
        if not self.connected:
            await self.connect()
        
        try:
            analog_results = self.plc.read(*self.analog_tags)
            boolean_results = self.plc.read(*self.boolean_tags)
            
            if analog_results is None and boolean_results is None:
                print("Error: PLC returned None for all values")
                self.connected = False
                return None
                
            tag_data = {'analog': {}, 'boolean': {}}
            timestamp = datetime.now()
            
            for tag, result in zip(self.analog_tags, analog_results):
                if result and result.value is not None:
                    await save_reading(tag, result.value, timestamp)
                    tag_data['analog'][tag] = result.value
            
            for tag, result in zip(self.boolean_tags, boolean_results):
                if result and result.value is not None:
                    await save_reading(tag, int(result.value), timestamp)
                    tag_data['boolean'][tag] = bool(result.value)
            
            return {
                'timestamp': timestamp.isoformat(),
                'values': tag_data
            }
            
        except Exception as e:
            print(f"Error reading PLC: {e}")
            self.connected = False
            return None

    def close(self):
        if self.plc:
            try:
                self.plc.close()
            except Exception as e:
                print(f"Error closing PLC connection: {e}")
            finally:
                self.connected = False

plc_monitor = PLCMonitor('10.109.99.124')

@app.route("/")
async def home():
    return await render_template("index.html")

@app.route("/history")
async def history():
    return await render_template("history.html")

@app.websocket('/ws')
async def ws():
    try:
        while True:
            data = await plc_monitor.read_data()
            if data:
                await websocket.send_json(data)
            await asyncio.sleep(1)
    except Exception as e:
        print(f"WebSocket error: {e}")

@app.route("/api/history")
async def get_history():
    try:
        start = request.args.get('start')
        end = request.args.get('end')
        
        print(f"\nReceived date range request:")
        print(f"Start: {start}")
        print(f"End: {end}")
        
        if not start or not end:
            return {"error": True, "message": "Start and end dates are required"}, 400
            
        start_dt = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
        end_dt = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
        
        print(f"Parsed dates successfully:")
        print(f"Start: {start_dt}")
        print(f"End: {end_dt}")
        
        all_data = []
        for tag in plc_monitor.analog_tags:
            tag_data = await get_historical_data(tag, start_dt, end_dt)
            if tag_data:
                for reading in tag_data:
                    timestamp = reading['timestamp']
                    if isinstance(timestamp, str):
                        timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
                    all_data.append({
                        'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        'tag_name': tag,
                        'value': reading['value']
                    })
        
        if not all_data:
            print("No data found: No historical data available")
            return {"error": True, "message": "No historical data available"}, 404
            
        all_data.sort(key=lambda x: x['timestamp'])
        actual_start = min(x['timestamp'] for x in all_data)
        actual_end = max(x['timestamp'] for x in all_data)
        
        print(f"Returning {len(all_data)} records")
        print(f"Actual data range - Start: {actual_start}, End: {actual_end}")
        
        return {
            "data": all_data,
            "query_range": {
                "start": start_dt.strftime('%Y-%m-%d %H:%M:%S'),
                "end": end_dt.strftime('%Y-%m-%d %H:%M:%S')
            },
            "actual_range": {
                "start": actual_start,
                "end": actual_end
            }
        }
        
    except Exception as e:
        print(f"Error fetching historical data: {e}")
        return {"error": True, "message": str(e)}, 500

# Add this to initialize the database at startup
@app.before_serving
async def startup():
    """Initialize the database before the app starts"""
    print("Initializing database...")
    await init_db()
    print("Database initialized")

if __name__ == "__main__":
    print("Running server...")
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000,
        use_reloader=True
    )