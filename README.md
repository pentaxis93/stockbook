# StockBook

Personal stock trading tracker for managing family investments with portfolio analytics and performance monitoring.

## Overview

StockBook is a lightweight web application built with Python and Streamlit to help track personal and family stock investments. It provides a simple interface for recording trades, monitoring portfolio performance, and analyzing investment history.

## Features (Planned)

- 📊 Portfolio overview dashboard
- 📝 Trade entry and management
- 📈 Performance tracking
- 💰 Profit/loss calculations
- 📅 Historical data analysis
- 👨‍👩‍👧‍👦 Multi-account support for family members

## Tech Stack

- **Python** - Core programming language
- **Streamlit** - Web application framework
- **SQLite** - Local database for data persistence
- **Pandas** - Data manipulation and analysis

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/stockbook.git
cd stockbook

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Run the application
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`.

## Project Structure

```
stockbook/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── database/             # Database files and schema
├── utils/                # Utility modules
└── docs/                 # Additional documentation
```

## Development Status

🚧 **Early Development** - This project is in active development. Core features are being implemented.

## Contributing

This is a personal project, but suggestions and feedback are welcome through issues.

## License

MIT License - see LICENSE file for details.

## Disclaimer

This software is for personal use only and should not be considered financial advice. Always consult with qualified financial professionals for investment decisions.
