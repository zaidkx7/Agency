import os
import re
import csv
import json
import requests

from bs4 import BeautifulSoup
from logger import get_logger
from urllib.parse import urljoin


__all__ = ['AgencyScraper']


class AgencyScraper:
    BASE_URL: str = "https://www.lefeuvre-immobilier.com"
    MODULE: str = 'AGENCY'
    PROJECT_DIR: str = os.path.dirname(os.path.abspath(__file__))
    FILES_DIR: str = os.path.join(PROJECT_DIR, 'files')
    if not os.path.exists(FILES_DIR):
        os.makedirs(FILES_DIR)
    AGENCIES_INFO: list = []
    HEADERS: list = ['ID', 'Agency Link', 'Agency', 'Services', 'Address', 'Phone', 'Hours']

    def __init__(self) -> None:
        self.logger = get_logger(self.MODULE)
        self.logger.info("Initializing AgencyScraper...")

    def get_page(self, url: str) -> str:
        response = requests.get(url)
        response.raise_for_status()
        return response.text

    def fetch_agency_links(self):
        """Fetches all agency links from the base URL."""
        page = self.get_page(urljoin(self.BASE_URL, '/lentreprise/nos-agences-de-proximite'))
        soup = BeautifulSoup(page, 'html.parser')
        agency_links: list = []
        for a_tag in soup.find_all('a', title="Consulter la fiche de l'agence"):
            href = a_tag.get('href')
            if href:
                agency_links.append(urljoin(self.BASE_URL, href))
        self.logger.info("Found %s agency links." % len(agency_links))
        return agency_links

    def fetch_agency_data(self, url: str) -> dict:
        """Fetches data for an individual agency."""
        temp_title = url.split('/')[-1].replace('-', ' ').title()
        self.logger.info('Getting data for agency %s' % temp_title)
        page = self.get_page(url)
        soup = BeautifulSoup(page, 'html.parser')
        inner_div = soup.find('div', class_='informations to-match')
        if not inner_div:
            self.logger.error('No inner div found for agency %s' % temp_title)
            return None
        
        agency_title = inner_div.find('h2', itemprop='name').text if inner_div.find('h2', itemprop='name') else 'Not available'
        agency_services = inner_div.find('p', class_='services').text if inner_div.find('p', class_='services') else 'Not available'
        agency_address = inner_div.find('p', class_='adresse').text if inner_div.find('p', class_='adresse') else 'Not available'

        phone_tag = inner_div.find('p', class_='telephone')
        phone_numbers: list = re.findall(r'\d{2} \d{2} \d{2} \d{2} \d{2}', phone_tag.get_text()) if phone_tag else []
        agency_phone = ', '.join(phone_numbers)

        hours_tag = inner_div.find('p', class_='horaires')
        agency_hours = hours_tag.get_text().replace("Horaires d'ouverture :", '').strip() if hours_tag else 'Not available'

        self.logger.info('Got data for agency %s' % agency_title)
        return {
            'Agency Link': url,
            'Agency': agency_title,
            'Services': agency_services,
            'Address': agency_address,
            'Phone': agency_phone,
            'Hours': agency_hours
        }

    def save_to_csv(self, agencies_info: list, file_name: str):
        """Saves agency information to a CSV file."""
        with open(f'{self.FILES_DIR}/{file_name}.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.HEADERS)
            writer.writeheader()
            
            for idx, agency in enumerate(agencies_info, start=1):
                row_data = {
                    'ID': idx,
                    'Agency Link': agency['Agency Link'],
                    'Agency': agency['Agency'],
                    'Services': agency['Services'],
                    'Address': agency['Address'],
                    'Phone': agency['Phone'],
                    'Hours': agency['Hours']
                }
                writer.writerow(row_data)
            
            self.logger.info("Agencies info saved to CSV %s" % f'{self.FILES_DIR}/{file_name}.csv')

    def save_to_json(self, data: list, file_name: str):
        """Saves agency information to a JSON file."""
        with open(f'{self.FILES_DIR}/{file_name}.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        self.logger.info("Agencies info saved to JSON %s" % f'{self.FILES_DIR}/{file_name}.json')

    def run(self) -> None:
        self.logger.info("Starting Agency Scraper...")
        agency_links = self.fetch_agency_links()
        for link in agency_links:
            agency_data = self.fetch_agency_data(link)
            if agency_data:
                self.AGENCIES_INFO.append(agency_data)
        
        if self.AGENCIES_INFO:
            self.save_to_csv(self.AGENCIES_INFO, 'agencies_info')
            self.save_to_json(self.AGENCIES_INFO, 'agencies_info')
            self.logger.info('Agencies info saved to CSV and JSON files')
            self.logger.info('Agency Scraper Completed')
            return
        
        self.logger.error('No agency data was collected')
        return


def run():
    return AgencyScraper()

if __name__ == "__main__":
    run().run()
