import requests
import logging
import random
import json
from django import template
from django.core.cache import cache

register = template.Library()
logger = logging.getLogger(__name__)

@register.simple_tag
def versiculo_aleatorio():
    # Try to get Bible data from cache first
    bible_data = cache.get('bible_data')
    
    if not bible_data:
        try:
            # Fetch Bible data from GitHub
            url = "https://raw.githubusercontent.com/MaatheusGois/bible/main/versions/pt-br/nvi.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                content = response.content.decode('utf-8-sig')
                bible_data = json.loads(content)
                # Log structure for debugging
                logger.info(f"Bible data type: {type(bible_data)}")
                if isinstance(bible_data, list) and len(bible_data) > 0:
                    logger.info(f"First item type: {type(bible_data[0])}")
                
                # Cache the data for 24 hours (86400 seconds)
                cache.set('bible_data', bible_data, 86400)
                logger.info("Successfully fetched and cached Bible data")
            else:
                logger.error(f"Failed to fetch Bible data: Status code {response.status_code}")
                return "Cada um dê conforme determinou em seu coração (2 Coríntios 9:7)"
                
        except Exception as e:
            logger.error(f"Error fetching Bible data: {str(e)}")
            print(f"Bible data fetch error: {str(e)}")
            return "Cada um dê conforme determinou em seu coração (2 Coríntios 9:7)"
    
    try:
        # Handle the data based on its structure
        if isinstance(bible_data, list):
            # Assume structure is a list of books
            # Each book is likely a dict with name, chapters, etc.
            book = random.choice(bible_data)
            
            # Log book structure to understand format
            print(f"Book structure: {list(book.keys() if isinstance(book, dict) else ['Not a dict'])}")
            
            # Try to extract necessary information based on common structures
            if isinstance(book, dict):
                book_name = book.get('name', '')
                chapters = book.get('chapters', [])
                
                if chapters and isinstance(chapters, list):
                    chapter = random.choice(chapters)
                    chapter_num = chapters.index(chapter) + 1  # 1-based chapter index
                    
                    if isinstance(chapter, list):
                        verse_index = random.randint(0, len(chapter) - 1)
                        verse_text = chapter[verse_index]
                        verse_num = verse_index + 1  # 1-based verse index
                        
                        return f"{book_name} {chapter_num}:{verse_num} - {verse_text}"
        
        # If we reached here, the structure is not what we expected
        # Let's use a fallback approach by inspecting and adapting
        print(f"Using fallback approach. JSON structure: {type(bible_data)}")
        
        # For list structure
        if isinstance(bible_data, list) and len(bible_data) > 0:
            # Select random item and try to make something meaningful
            random_item = random.choice(bible_data)
            if isinstance(random_item, dict):
                # Try common field names for verses in various formats
                possibilities = [
                    # Format: {book} {chapter}:{verse} - {text}
                    f"{random_item.get('book', '')} {random_item.get('chapter', '')}:{random_item.get('verse', '')} - {random_item.get('text', '')}",
                    # Format: {name} {chapter}:{verse} - {content}
                    f"{random_item.get('name', '')} {random_item.get('chapter', '')}:{random_item.get('verse', '')} - {random_item.get('content', '')}"
                ]
                
                # Use first non-empty format
                for p in possibilities:
                    if not all(x in ['', ' ', ':', '-'] for x in p):
                        return p
        
        # If all else fails
        return "Cada um dê conforme determinou em seu coração (2 Coríntios 9:7)"
        
    except Exception as e:
        logger.error(f"Error selecting random verse: {str(e)}")
        print(f"Random verse selection error: {str(e)}")
        return "Cada um dê conforme determinou em seu coração (2 Coríntios 9:7)"