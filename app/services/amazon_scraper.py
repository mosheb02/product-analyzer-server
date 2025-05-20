import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import json
from datetime import datetime
import time
import random

class AmazonScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }

    async def get_product_reviews(self, product_url: str, max_reviews: int = 50) -> Dict:
        try:
            # Extract product ID from URL
            product_id = self._extract_product_id(product_url)
            if not product_id:
                raise ValueError("Invalid Amazon product URL")

            reviews = []
            page = 1
            
            while len(reviews) < max_reviews:
                review_url = f"https://www.amazon.com/product-reviews/{product_id}/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews&pageNumber={page}"
                
                response = requests.get(review_url, headers=self.headers)
                if response.status_code != 200:
                    break

                soup = BeautifulSoup(response.text, 'html.parser')
                review_elements = soup.find_all('div', {'data-hook': 'review'})
                
                if not review_elements:
                    break

                for review in review_elements:
                    if len(reviews) >= max_reviews:
                        break

                    review_data = {
                        'rating': self._extract_rating(review),
                        'title': self._extract_title(review),
                        'text': self._extract_text(review),
                        'date': self._extract_date(review),
                        'verified': self._is_verified(review)
                    }
                    reviews.append(review_data)

                page += 1
                # Respect Amazon's rate limiting
                time.sleep(random.uniform(1, 3))

            return {
                'product_id': product_id,
                'total_reviews': len(reviews),
                'reviews': reviews,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def _extract_product_id(self, url: str) -> Optional[str]:
        # Extract product ID from Amazon URL
        # Example URL: https://www.amazon.com/dp/B08N5KWB9H
        try:
            if '/dp/' in url:
                return url.split('/dp/')[1].split('/')[0]
            elif '/gp/product/' in url:
                return url.split('/gp/product/')[1].split('/')[0]
            return None
        except:
            return None

    def _extract_rating(self, review_element) -> float:
        try:
            rating_text = review_element.find('i', {'data-hook': 'review-star-rating'}).text
            return float(rating_text.split(' out of')[0])
        except:
            return 0.0

    def _extract_title(self, review_element) -> str:
        try:
            return review_element.find('a', {'data-hook': 'review-title'}).text.strip()
        except:
            return ""

    def _extract_text(self, review_element) -> str:
        try:
            return review_element.find('span', {'data-hook': 'review-body'}).text.strip()
        except:
            return ""

    def _extract_date(self, review_element) -> str:
        try:
            return review_element.find('span', {'data-hook': 'review-date'}).text.strip()
        except:
            return ""

    def _is_verified(self, review_element) -> bool:
        try:
            return bool(review_element.find('span', {'data-hook': 'avp-badge'}))
        except:
            return False 