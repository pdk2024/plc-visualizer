# PLC Visualizer

A real-time web application for visualizing Allen Bradley PLC data using Quart framework and PyComm3.

## Overview
Currently monitoring steam tunnel control parameters with plans to expand to production metrics monitoring.

## Current Features

### Steam Tunnel Monitoring
- [x] Real-time PLC data collection and visualization
- [x] WebSocket updates (3-second intervals)
- [x] Historical data storage with SQLite
- [x] Network accessibility (0.0.0.0)
- [x] Optimized PLC reading method

### Technical Implementation
#### Backend
- [x] Quart web framework implementation
- [x] PyComm3 PLC communication
- [x] Basic error handling and reconnection logic
- [x] Database integration

#### Frontend
- [x] Real-time line charts using Chart.js
- [x] Connection status indicator
- [x] Automatic data point limiting (100 points)
- [x] Responsive design
- [x] Auto-reconnect on connection loss

### PLC Configuration
- Steam Tunnel PLC (IP: 10.109.99.124)
- Tags Monitored:
  - CV31027_PIDE.SP/PV (Pressure)
  - CV31028_PIDE.SP/PV (Temperature)
  - CV31029_PIDE.SP/PV (Flow)

## Planned Features

### Production Monitoring (Coming Soon)
- [ ] Production PLC Integration (IP: 192.168.1.113)
- [ ] Shift-based production

## Setup

1. Install Poetry (package manager):

curl -sSL https://install.python-poetry.org | python3 -

2. Clone the repository:

git clone https://github.com/pdk2024/plc-visualizer.git

cd plc-visualizer

3. Install dependencies:

poetry install

4. Run the application:

poetry run python src/plc_visualizer/app.py

##Project Structure  

plc-visualizer/
├── src/
│ └── plc_visualizer/
│ ├── init.py
│ ├── app.py # Main application
│ ├── database.py # Database operations
│ ├── models/ # Database models
│ └── templates/ # HTML templates
├── pyproject.toml
├── poetry.lock
└── README.md

## Dependencies

### Production
- Quart: Web framework
- PyComm3: PLC communication
- SQLAlchemy: Database ORM
- Chart.js: Data visualization

### Development
- pytest: Testing
- black: Code formatting
- flake8: Linting
- isort: Import sorting

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
[MIT License](LICENSE)

## Contact
Project maintained by PDK


