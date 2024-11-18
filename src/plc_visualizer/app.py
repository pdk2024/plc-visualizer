from quart import Quart, render_template, websocket, request
from pathlib import Path
import sys
import asyncio
from pycomm3 import LogixDriver
import json
from datetime import datetime

# Use relative import instead
from .database import init_db, save_reading, get_historical_data, get_tag_metadata, update_tag_metadata

print("Starting application...")
print(f"Python version: {sys.version}")

class PLCMonitor:
    def __init__(self, ip_address):
        self.ip_address = ip_address
        self.plc = None
        self.connected = False
        self.tags = [
            'CV31027_PIDE.SP',
            'CV31027_PIDE.PV',
            'CV31028_PIDE.SP',
            'CV31028_PIDE.PV',
            'CV31029_PIDE.SP',
            'CV31029_PIDE.PV'
        ]

    async def connect(self):
        try:
            print(f"Connecting to PLC at {self.ip_address}...")
            self.plc = LogixDriver(self.ip_address)
            self.plc.open()
            self.connected = True
            print("Connected to PLC successfully")
            return True
        except Exception as e:
            print(f"Error connecting to PLC: {e}")
            self.connected = False
            return False

    async def read_data(self):
        if not self.connected:
            await self.connect()
        
        try:
            # Read all tags in a single request
            results = self.plc.read(*self.tags)
            
            if results is None:
                print("Error: PLC returned None for values")
                self.connected = False
                return None
                
            tag_data = {}
            timestamp = datetime.now()
            
            # Process results
            for tag, result in zip(self.tags, results):
                if result is None or result.value is None:
                    print(f"Error: Invalid value for tag {tag}")
                    continue
                    
                try:
                    metadata = await get_tag_metadata(tag)
                    if metadata is None:
                        print(f"Error: No metadata found for tag {tag}")
                        continue
                        
                    await save_reading(timestamp, tag, result.value)
                    tag_data[tag] = result.value
                    
                except Exception as e:
                    print(f"Error processing tag {tag}: {e}")
                    continue
            
            if tag_data:
                return {
                    'timestamp': timestamp.isoformat(),
                    'values': tag_data
                }
            return None
            
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

app = Quart(__name__)
plc_monitor = PLCMonitor('10.109.99.124')

# Template directory configuration
app.template_folder = Path(__file__).parent / "templates"
app.static_folder = Path(__file__).parent / "static"

@app.before_serving
async def startup():
    """Initialize the database before the app starts"""
    await init_db()
    print("Database initialized")

@app.websocket('/ws')
async def ws():
    try:
        await plc_monitor.connect()
        while True:
            data = await plc_monitor.read_data()
            if data:
                await websocket.send(json.dumps(data))
            await asyncio.sleep(3)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        plc_monitor.close()

@app.route("/")
async def index():
    return await render_template("index.html")

@app.route("/history")
async def history_page():
    return await render_template("history.html")

@app.route("/api/history")
async def get_history():
    try:
        start = request.args.get('start')
        end = request.args.get('end')
        
        if not start or not end:
            return {"error": True, "message": "Start and end dates are required"}, 400
            
        # Parse datetime strings
        start_dt = datetime.strptime(start, '%Y-%m-%d %H:%M')
        end_dt = datetime.strptime(end, '%Y-%m-%d %H:%M')
        
        # Get historical data for all tags
        tags = [
            'CV31027_PIDE.SP', 'CV31027_PIDE.PV',  # Pressure
            'CV31028_PIDE.SP', 'CV31028_PIDE.PV',  # Temperature
            'CV31029_PIDE.SP', 'CV31029_PIDE.PV'   # Flow
        ]
        
        all_data = []
        for tag in tags:
            tag_data = await get_historical_data(tag, start_dt, end_dt)
            for reading in tag_data:
                all_data.append({
                    'timestamp': reading['timestamp'],
                    'tag_name': tag,
                    'value': reading['value']
                })
        
        # Sort by timestamp
        all_data.sort(key=lambda x: x['timestamp'])
        
        return all_data
        
    except Exception as e:
        print(f"Error fetching historical data: {e}")
        return {"error": True, "message": str(e)}, 500

if __name__ == "__main__":
    print("Running server...")
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000,
        use_reloader=True
    )