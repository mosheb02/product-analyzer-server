from langchain.tools import BaseTool
from typing import Dict, Any
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSearchTool(BaseTool):
    name: str = "web_search"
    description: str = "Search the web for information about products and companies"

    async def _run(self, query: str) -> Dict[str, Any]:
        logger.info(f"WebSearchTool: Starting search with query: {query}")
        try:
            # Use a search API (you can replace this with your preferred search API)
            logger.info("WebSearchTool: Making request to Serper API")
            response = requests.get(
                f"https://api.serper.dev/search",
                headers={
                    "X-API-KEY": "c5fef1fe2d1c1d4ba974d3952c7ab4bd7c82ee0b",  # Replace with your API key
                    "Content-Type": "application/json"
                },
                json={"q": query}
            )
            
            if response.status_code != 200:
                error_msg = f"Search API error: {response.text}"
                logger.error(f"WebSearchTool: {error_msg}")
                raise Exception(error_msg)

            data = response.json()
            logger.info(f"WebSearchTool: Successfully retrieved {len(data.get('organic', []))} search results")
            return {
                'search_results': data.get('organic', []),
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"WebSearchTool: Error occurred: {str(e)}")
            return {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

class WebScrapingTool(BaseTool):
    name: str = "web_scrape"
    description: str = "Scrape product information from web pages"

    async def _run(self, url: str) -> Dict[str, Any]:
        logger.info(f"WebScrapingTool: Starting scrape for URL: {url}")
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            
            logger.info("WebScrapingTool: Making request to URL")
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                error_msg = f"Failed to fetch URL: {response.status_code}"
                logger.error(f"WebScrapingTool: {error_msg}")
                raise Exception(error_msg)

            logger.info("WebScrapingTool: Parsing HTML content")
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract product information
            logger.info("WebScrapingTool: Extracting product information")
            product_info = {
                'title': self._extract_title(soup),
                'price': self._extract_price(soup),
                'description': self._extract_description(soup),
                'reviews': self._extract_reviews(soup),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"WebScrapingTool: Successfully extracted product info: {json.dumps(product_info, indent=2)}")
            return product_info
        except Exception as e:
            logger.error(f"WebScrapingTool: Error occurred: {str(e)}")
            return {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def _extract_title(self, soup: BeautifulSoup) -> str:
        try:
            title = soup.find('h1').text.strip()
            logger.debug(f"WebScrapingTool: Extracted title: {title}")
            return title
        except Exception as e:
            logger.warning(f"WebScrapingTool: Failed to extract title: {str(e)}")
            return ""

    def _extract_price(self, soup: BeautifulSoup) -> str:
        try:
            price = soup.find('span', {'class': 'price'}).text.strip()
            logger.debug(f"WebScrapingTool: Extracted price: {price}")
            return price
        except Exception as e:
            logger.warning(f"WebScrapingTool: Failed to extract price: {str(e)}")
            return ""

    def _extract_description(self, soup: BeautifulSoup) -> str:
        try:
            description = soup.find('div', {'class': 'description'}).text.strip()
            logger.debug(f"WebScrapingTool: Extracted description: {description[:100]}...")
            return description
        except Exception as e:
            logger.warning(f"WebScrapingTool: Failed to extract description: {str(e)}")
            return ""

    def _extract_reviews(self, soup: BeautifulSoup) -> list:
        reviews = []
        try:
            review_elements = soup.find_all('div', {'class': 'review'})
            logger.info(f"WebScrapingTool: Found {len(review_elements)} review elements")
            for review in review_elements:
                review_data = {
                    'rating': self._extract_rating(review),
                    'text': self._extract_review_text(review),
                    'date': self._extract_review_date(review)
                }
                reviews.append(review_data)
        except Exception as e:
            logger.warning(f"WebScrapingTool: Failed to extract reviews: {str(e)}")
        return reviews

    def _extract_rating(self, review_element) -> float:
        try:
            rating = float(review_element.find('span', {'class': 'rating'}).text)
            logger.debug(f"WebScrapingTool: Extracted rating: {rating}")
            return rating
        except Exception as e:
            logger.warning(f"WebScrapingTool: Failed to extract rating: {str(e)}")
            return 0.0

    def _extract_review_text(self, review_element) -> str:
        try:
            text = review_element.find('div', {'class': 'review-text'}).text.strip()
            logger.debug(f"WebScrapingTool: Extracted review text: {text[:100]}...")
            return text
        except Exception as e:
            logger.warning(f"WebScrapingTool: Failed to extract review text: {str(e)}")
            return ""

    def _extract_review_date(self, review_element) -> str:
        try:
            date = review_element.find('span', {'class': 'review-date'}).text.strip()
            logger.debug(f"WebScrapingTool: Extracted review date: {date}")
            return date
        except Exception as e:
            logger.warning(f"WebScrapingTool: Failed to extract review date: {str(e)}")
            return "" 