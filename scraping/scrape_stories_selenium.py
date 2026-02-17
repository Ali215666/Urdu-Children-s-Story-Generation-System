from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import os
import re
import requests

# Data folder
data_folder = "data"
os.makedirs(data_folder, exist_ok=True)

def clean_filename(title):
    """Clean the title to make it a valid filename"""
    title = re.sub(r'[<>:"/\\|?*]', '', title)
    title = title.strip().replace(' ', '_')
    return title[:100] if len(title) > 100 else title

def scrape_story_content(story_url):
    """Scrape the content of a single story"""
    try:
        response = requests.get(story_url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the story title
        title_elem = soup.find('h1', class_='poemTitle') or soup.find('h1')
        title = title_elem.get_text(strip=True) if title_elem else "Untitled"
        
        # Find author
        author_elem = soup.find('a', class_='poetName') or soup.find('span', class_='author')
        author = author_elem.get_text(strip=True) if author_elem else "Unknown"
        
        # Find the story content
        content_div = soup.find('div', class_='poemPageContentBody')
        if not content_div:
            content_div = soup.find('div', class_='contentBody')
        if not content_div:
            content_div = soup.find('div', id='content')
        
        if content_div:
            story_text = content_div.get_text(separator='\n', strip=True)
            return {'title': title, 'author': author, 'content': story_text}
        return None
    except Exception as e:
        print(f"Error scraping story: {e}")
        return None

def get_all_story_urls():
    """Use Selenium to load all stories and extract URLs"""
    print("Setting up browser...")
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in background
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        url = "https://www.rekhta.org/tags/children-s-story/children-s-stories?lang=ur"
        print(f"Loading page: {url}")
        driver.get(url)
        
        # Wait for initial content to load
        time.sleep(5)
        
        story_urls = set()
        last_count = 0
        no_change_count = 0
        scroll_attempts = 0
        max_scrolls = 100  # Maximum scroll attempts
        
        print("Scrolling to load all stories...")
        print("(This may take several minutes - loading 200-300+ stories)")
        
        while no_change_count < 10 and scroll_attempts < max_scrolls:
            scroll_attempts += 1
            
            # Scroll to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Wait longer for content to load (6 seconds)
            time.sleep(6)
            
            # Also try scrolling in smaller increments
            for i in range(3):
                driver.execute_script(f"window.scrollBy(0, 500);")
                time.sleep(1)
            
            # Find all story links
            links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/children-s-stories/children-s-story/"]')
            
            for link in links:
                try:
                    href = link.get_attribute('href')
                    if href and 'javascript:void' not in href:
                        story_urls.add(href)
                except:
                    pass
            
            current_count = len(story_urls)
            print(f"Scroll {scroll_attempts}: Found {current_count} unique story URLs...")
            
            if current_count == last_count:
                no_change_count += 1
                print(f"  (No new stories for {no_change_count} consecutive scrolls)")
            else:
                no_change_count = 0
                print(f"  (+{current_count - last_count} new stories)")
            
            last_count = current_count
        
        print(f"\nTotal unique story URLs found: {len(story_urls)}")
        return list(story_urls)
        
    finally:
        driver.quit()

def main():
    """Main function to scrape all stories"""
    print("Starting to scrape Urdu children's stories...")
    print("=" * 60)
    
    # Step 1: Get all story URLs using Selenium
    story_urls = get_all_story_urls()
    
    if not story_urls:
        print("No story URLs found!")
        return
    
    print(f"\n{'='*60}")
    print(f"Starting to scrape {len(story_urls)} stories...")
    print(f"{'='*60}\n")
    
    # Step 2: Scrape each story
    story_count = 0
    for story_url in story_urls:
        story_count += 1
        print(f"\n[{story_count}/{len(story_urls)}] Scraping: {story_url}")
        
        # Get story content
        story_data = scrape_story_content(story_url)
        
        if story_data:
            # Save to file
            filename = clean_filename(story_data['title'])
            filepath = os.path.join(data_folder, f"{story_count:03d}_{filename}.txt")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Title: {story_data['title']}\n")
                f.write(f"Author: {story_data['author']}\n")
                f.write(f"URL: {story_url}\n")
                f.write("=" * 60 + "\n\n")
                f.write(story_data['content'])
            
            print(f"✓ Saved: {story_data['title'][:50]}")
        else:
            print(f"✗ Failed to get content")
        
        # Delay between requests
        time.sleep(2)
    
    print("\n" + "=" * 60)
    print(f"Scraping complete! Total stories saved: {story_count}")

if __name__ == "__main__":
    main()
