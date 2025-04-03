from bs4 import BeautifulSoup
import requests
import json
import re
from typing import Dict, Any
import logging

class APIStatusChecker:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win 64 ; x64) Apple WeKit /537.36(KHTML , like Gecko) Chrome/80.0.3987.162 Safari/537.36'
        }
        self.urls = {
            'openai': 'https://status.openai.com/',
            'gemini': 'https://status.cloud.google.com/',
            'llama': 'https://llamaindex.statuspage.io/',
            'claude': 'https://status.anthropic.com/'
        }
        self.soups = {}
        self._initialize_soups()

    def _initialize_soups(self):
        """Initialize BeautifulSoup objects for all APIs"""
        try:
            for name, url in self.urls.items():
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()  # Raise an exception for bad status codes
                self.soups[name] = BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            logging.error(f"Error initializing API status checker: {str(e)}")
            raise

    def check_openai_status(self) -> int:
        """Check OpenAI API status"""
        try:
            soup = self.soups['openai']
            text = soup.find_all('svg', {'class': 'mb-1'})[0].find_all('rect')[-1]
            return 1 if 'transition UptimeChart_pillOperational__sYJ07' in str(text) else 0
        except Exception as e:
            logging.error(f"Error checking OpenAI status: {str(e)}")
            return 0

    def check_gemini_status(self) -> int:
        """Check Google Cloud Gemini API status"""
        try:
            soup = self.soups['gemini']
            status_element = soup.findAll('tr')[-7].find_all('td')[2].find_all('svg')[0]
            return 1 if 'psd__status-icon psd__available' in str(status_element) else 0
        except Exception as e:
            logging.error(f"Error checking Gemini status: {str(e)}")
            return 0

    def check_llama_status(self) -> int:
        """Check LlamaIndex API status"""
        try:
            soup = self.soups['llama']
            text = soup.findAll('div', {'class': 'component-container border-color is-group'})[0].findAll('span')[8].get_text()
            text = re.sub(r'\s+', '', text)
            return 1 if text == 'Operational' else 0
        except Exception as e:
            logging.error(f"Error checking Llama status: {str(e)}")
            return 0

    def check_claude_status(self) -> int:
        """Check Anthropic Claude API status"""
        try:
            soup = self.soups['claude']
            text = soup.findAll('div', {"class": 'component-container border-color'})[0].findAll('span', {'class': 'component-status'})[0].get_text()
            text = re.sub(r'\s+', '', text)
            return 1 if text == "Operational" else 0
        except Exception as e:
            logging.error(f"Error checking Claude status: {str(e)}")
            return 0

    def get_all_statuses(self) -> Dict[str, Any]:
        """Get status of all APIs"""
        return {
            "OpenAI": self.check_openai_status(),
            "Claude": self.check_claude_status(),
            "Gemini": self.check_gemini_status(),
            "Llama": self.check_llama_status()
        } 