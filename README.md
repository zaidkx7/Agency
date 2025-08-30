# AgencyScraper

A Python tool that automatically collects information about real estate agencies from the `Lefeuvre Immobilier` website. It gathers agency names, contact details, services, and operating hours, saving everything to a CSV and JSON files. Perfect for anyone who needs to keep track of real estate agency information or analyze market data.

## Description

This tool automatically scrapes information about real estate agencies, including:
- Agency names
- Services offered
- Addresses
- Phone numbers
- Operating hours

The scraped data is saved in a CSV and JSON files for easy access and analysis.

## Features

- Automated scraping of agency information
- Data extraction from individual agency pages
- CSV export with structured data
- JSON structured data 
- Logging functionality for monitoring the scraping process
- Error handling and validation

## Requirements

- Python 3.x
- Required Python packages:
  - requests
  - beautifulsoup4
  - csv
  - os
  - re
  - sys

## Installation

1. Clone the repository:
```bash
git clone https://github.com/zaidkx7/Agency.git
cd Agency
```

2. Install the required dependencies:
```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Simply run the main script:
```bash
python main.py
```

The script will:
1. Fetch all agency links from the base URL
2. Visit each agency page and extract relevant information
3. Save the collected data to a CSV file in the `response` directory

## Output

The script generates a CSV (`agencies_info.csv`) and JSON (`agencies_info.json`) files in the `files` directory with the following columns:
- ID
- Agency Link
- Agency Name
- Services
- Address
- Phone
- Hours

## Project Structure

```
AgencyScraper/
├── main.py
├── logger.py
├── files/
│   └── agencies_info.csv
|   └── agencies_info.json
└── README.md
```

## Notes

- The scraper respects the website's structure and extracts data from the designated HTML elements
- All data is saved with UTF-8 encoding to properly handle French characters
- The script includes error handling and logging for monitoring the scraping process

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 