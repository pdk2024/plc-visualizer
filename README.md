# PLC Visualizer

A real-time web application for visualizing Allen Bradley PLC data using Quart framework and PyComm3.

## Current Features

### Backend
- [x] Quart web framework implementation
- [x] PyComm3 PLC communication
- [x] WebSocket real-time updates
- [x] Configurable update interval (currently 3 seconds)
- [x] Basic error handling and reconnection logic

### Frontend
- [x] Real-time line chart using Chart.js
- [x] Connection status indicator
- [x] Automatic data point limiting (100 points)
- [x] Responsive design
- [x] Auto-reconnect on connection loss

### PLC Communication
- [x] Connection to Allen Bradley PLC (IP: 10.109.99.124)
- [x] Monitoring Steam Tunnel parameters:
  - Steam Temperature Setpoint (CV31027_PIDE.SP)
  - Steam Temperature Process Value (CV31027_PIDE.PV)

## TODO List

### Backend Enhancements
- [ ] Add configuration file for PLC settings
- [ ] Implement logging system
- [ ] Add data persistence/historical data
- [ ] Implement authentication system
- [ ] Add API endpoints for configuration changes
- [ ] Add unit tests
- [ ] Add error reporting system

### Frontend Improvements
- [ ] Add data export functionality
- [ ] Implement zoom/pan controls for chart
- [ ] Add multiple chart types/views
- [ ] Add real-time statistics (min, max, average)
- [ ] Add dark mode support
- [ ] Add mobile-friendly optimizations
- [ ] Add configuration UI for:
  - Update interval
  - Number of data points
  - Chart appearance

### PLC Communication
- [ ] Add support for multiple PLCs
- [ ] Implement tag discovery
- [ ] Add tag validation
- [ ] Add communication diagnostics
- [ ] Implement write capabilities (if needed)
- [ ] Add tag aliasing/mapping

### DevOps & Deployment
- [ ] Add Docker support
- [ ] Create deployment documentation
- [ ] Add CI/CD pipeline
- [ ] Implement monitoring/health checks
- [ ] Add backup/restore functionality

## Setup

1. Install Poetry (package manager):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Clone the repository:
```bash
git clone <repository-url>
cd plc-visualizer
```

3. Install dependencies:
```bash
poetry install
```

4. Run the application:
```bash
poetry run python src/plc_visualizer/app.py
```

## Project Structure
```
plc-visualizer/
├── pyproject.toml
├── README.md
└── src/
    └── plc_visualizer/
        ├── __init__.py
        ├── app.py
        └── templates/
            └── index.html
```

## Dependencies

### Production
- Quart: Web framework
- PyComm3: PLC communication
- Python-dotenv: Environment management

### Development
- pytest: Testing
- black: Code formatting
- flake8: Linting
- isort: Import sorting

## Configuration

Current configuration is hardcoded in the application:
- PLC IP: 10.109.99.124
- Update Interval: 3 seconds
- Max Data Points: 100

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license here]

## Contact

[Add your contact information]
