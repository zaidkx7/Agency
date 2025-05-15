import os
import csv
import requests
import re
import sys

from bs4 import BeautifulSoup
from clogger import get_logger


__all__ = ['AgencyScraper']


class AgencyScraper:
    BASE_URL = "https://www.lefeuvre-immobilier.com/lentreprise/nos-agences-de-proximite"
    PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
    RESPONSE_DIR = os.path.join(PROJECT_DIR, 'response')
    if not os.path.exists(RESPONSE_DIR):
        os.makedirs(RESPONSE_DIR)
    DATA_FILE = os.path.join(RESPONSE_DIR, 'agencies_info.csv')
    SESSION = requests.Session()
    AGENCIES_INFO = []
    HEADERS = ['ID', 'Agency Link', 'Agency', 'Services', 'Address', 'Phone', 'Hours']

    def __init__(self):
        self.logger = get_logger()
        self.logger.info("Initializing AgencyScraper...")

    def get_page(self, url):
        response = self.SESSION.get(url)
        response.raise_for_status()
        return response.text

    def fetch_agency_links(self):
        """Fetches all agency links from the base URL."""
        page = self.get_page(self.BASE_URL)
        soup = BeautifulSoup(page, 'html.parser')
        agency_links = []
        for a_tag in soup.find_all('a', title="Consulter la fiche de l'agence"):
            href = a_tag.get('href')
            if href:
                full_url = f"https://www.lefeuvre-immobilier.com{href}"
                agency_links.append(full_url)
        self.logger.info(f"Found {len(agency_links)} agency links.")
        return agency_links

    def fetch_agency_data(self, url):
        """Fetches data for an individual agency."""
        page = self.get_page(url)
        soup = BeautifulSoup(page, 'html.parser')
        inner_div = soup.find('div', class_='informations to-match')
        if not inner_div:
            return None
        
        agency_title = inner_div.find('h2', itemprop='name').text if inner_div.find('h2', itemprop='name') else "Not available"
        agency_services = inner_div.find('p', class_='services').text if inner_div.find('p', class_='services') else "Not available"
        agency_address = inner_div.find('p', class_='adresse').text if inner_div.find('p', class_='adresse') else "Not available"

        # Extract phone numbers
        phone_tag = inner_div.find('p', class_='telephone')
        phone_numbers = re.findall(r'\d{2} \d{2} \d{2} \d{2} \d{2}', phone_tag.get_text()) if phone_tag else []
        agency_phone = ', '.join(phone_numbers)

        # Extract hours of operation text
        hours_tag = inner_div.find('p', class_='horaires')
        agency_hours = hours_tag.get_text().replace("Horaires d'ouverture :", '').strip() if hours_tag else "Not available"

        return {
            'Agency Link': url,
            'Agency': agency_title,
            'Services': agency_services,
            'Address': agency_address,
            'Phone': agency_phone,
            'Hours': agency_hours
        }

    def save_agencies_info(self, agencies_info):
        """Saves agency information to a CSV file."""
        with open(self.DATA_FILE, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.HEADERS)
            writer.writeheader()
            
            for idx, agency in enumerate(agencies_info, start=1):
                row_data = {
                    'ID': idx,
                    'Agency Link': agency.get('Agency Link', ''),
                    'Agency': agency.get('Agency', ''),
                    'Services': agency.get('Services', ''),
                    'Address': agency.get('Address', ''),
                    'Phone': agency.get('Phone', ''),
                    'Hours': agency.get('Hours', '')
                }
                writer.writerow(row_data)
            
            self.logger.info(f"Agencies info saved to CSV: {self.DATA_FILE}")

    def run(self):
        self.logger.info("Starting to scrape agencies")
        agency_links = self.fetch_agency_links()
        
        for link in agency_links:
            agency_data = self.fetch_agency_data(link)
            if agency_data:
                self.AGENCIES_INFO.append(agency_data)
        
        if self.AGENCIES_INFO:
            self.save_agencies_info(self.AGENCIES_INFO)
            sys.exit(0)
        
        self.logger.error("No agency data was collected")


if __name__ == "__main__":
    AgencyScraper().run()
