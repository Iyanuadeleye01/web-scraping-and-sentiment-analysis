# Import the necessary libraries
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
import time
import pandas as pd
import random
import os
import json

# Session directory to maintain cookies between runs
SESSION_DIR = os.path.join(os.getcwd(), "chrome_session")
os.makedirs(SESSION_DIR, exist_ok=True)

# File to store checkpoint data
CHECKPOINT_FILE = "scraper_checkpoint.json"

def setup_driver():
    """Set up the undetected Chrome driver with necessary options"""
    options = uc.ChromeOptions()
    
    # Add user data directory to maintain session/cookies
    options.add_argument(f"--user-data-dir={SESSION_DIR}")
    
    # Make browser less detectable
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    # Use a realistic user agent
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36")
    
    
    # Initialize with undetected-chromedriver which helps bypass Cloudflare
    driver = uc.Chrome(options=options)
    
    # Set page load timeout
    driver.set_page_load_timeout(30)
    
    return driver

def random_sleep(min_seconds=2, max_seconds=5):
    """Sleep for a random amount of time to appear more human-like"""
    time.sleep(random.uniform(min_seconds, max_seconds))

def human_like_scroll(driver):
    """Scroll down the page in a human-like manner"""
    total_height = driver.execute_script("return document.body.scrollHeight")
    viewport_height = driver.execute_script("return window.innerHeight")
    
    # Scroll down in small increments with random pauses
    current_position = 0
    while current_position < total_height:
        scroll_increment = random.randint(100, 800)
        current_position += scroll_increment
        if current_position > total_height:
            current_position = total_height
        
        driver.execute_script(f"window.scrollTo(0, {current_position});")
        random_sleep(0.5, 1.5)

def scrape_page(driver, scraped_data):
    """Scrape the current page for articles"""
    # To check if we are on a valid page
    if "Just a moment" in driver.title:
        print("Still on Cloudflare challenge page. Waiting...")
        # Wait longer for Cloudflare to resolve
        time.sleep(15)
        return False
    
    print(f"Current page title: {driver.title}")
    
    # This add human-like behavior - scroll the page
    human_like_scroll(driver)
    
    
    try:
        # To wait for the news container to be present
        news_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.news"))
        )
        
        # Find all news items
        news_items = news_container.find_elements(By.XPATH, './/div[@class="post-info"]')
        print(f"Found {len(news_items)} news items")
        
        if not news_items:
            print("No news items found on the page.")
            return False
            
        # Process each news item
        for item in news_items:
            try:
                title = item.find_element(By.TAG_NAME, 'h2').find_element(By.TAG_NAME, 'a').text
                author = item.find_element(By.CLASS_NAME, 'post-author').find_element(By.TAG_NAME, 'a').text
                date = item.find_element(By.CLASS_NAME, 'post-date').text
                excerpt = item.find_element(By.TAG_NAME, 'p').text
                
                # Check if this item is already in scraped_data to avoid duplicates
                if not any(title == row[0] for row in scraped_data):
                    scraped_data.append([title, author, date, excerpt])
                    print(f"Added article: {title[:50]}...")
                else:
                    print(f"Skipping duplicate article: {title[:50]}...")
            except Exception as e:
                print(f"Error processing news item: {e}")
                continue
                
        return True
        
    except Exception as e:
        print(f"Error scraping page: {e}")
        return False

def save_checkpoint(page_count, scraped_data, current_url):
    """Save the current state of the scraper"""
    checkpoint = {
        "page_count": page_count,
        "current_url": current_url,
        "last_update": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump(checkpoint, f)
    
    # Save current data
    temp_df = pd.DataFrame(scraped_data, columns=['Title', 'Author', 'Date', 'Excerpt'])
    temp_df.to_csv('businessday_progress3.csv', index=False)
    print(f"Checkpoint saved: Page {page_count}, {len(scraped_data)} articles")

def load_checkpoint():
    """Load the previous checkpoint if it exists"""
    if not os.path.exists(CHECKPOINT_FILE):
        return None
    
    try:
        with open(CHECKPOINT_FILE, 'r') as f:
            checkpoint = json.load(f)
        return checkpoint
    except Exception as e:
        print(f"Error loading checkpoint: {e}")
        return None

def load_existing_data():
    """Load existing scraped data if it exists"""
    if os.path.exists('businessday_progress3.csv'):
        try:
            df = pd.read_csv('businessday_progress3.csv')
            return df.values.tolist()
        except Exception as e:
            print(f"Error loading existing data: {e}")
            return []
    return []

def main():
    print("Starting the scraper...")
    
    # Load checkpoint if it exists
    checkpoint = load_checkpoint()
    if checkpoint:
        page_count = checkpoint.get("page_count", 1)
        start_url = checkpoint.get("current_url")
        print(f"Resuming from checkpoint: Page {page_count}, URL: {start_url}")
    else:
        page_count = 1
        start_url = 'https://businessday.ng/tag/bdlead/?amp'
        print(f"No checkpoint found. Starting from page {page_count}")
    
    # Load existing data
    scraped_data = load_existing_data()
    print(f"Loaded {len(scraped_data)} previously scraped articles")
    
    # Setup the driver
    driver = setup_driver()
    
    try:
        # Navigate to the starting page
        print(f"Navigating to {start_url}")
        driver.get(start_url)
        
        # Wait for initial page load and let user solve CAPTCHA if needed
        print("Initial page loaded. If you see a CAPTCHA or Cloudflare challenge, please solve it manually.")
        print("You have 30 seconds to solve any challenges...")
        time.sleep(30)
        
        # Start scraping
        max_pages = 818
        
        while page_count <= max_pages:
            print(f"\nProcessing page {page_count}")
            
            # Get current URL before scraping
            current_url = driver.current_url
            
            # Scrape the current page
            if scrape_page(driver, scraped_data):
                print(f"Successfully scraped page {page_count}")
            else:
                print(f"Failed to scrape page {page_count}")
            
            # Save checkpoint after each page
            save_checkpoint(page_count, scraped_data, current_url)
            
            # Break if we have reached our target
            if page_count >= max_pages:
                break
                
            # To navigate to the next page
            try:
                print("Looking for next page button...")
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//a[@class="next page-numbers"]'))
                )
                
                # Scroll to the button
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                random_sleep(1, 2)
                
                # Click the button
                print("Clicking next page button...")
                driver.execute_script("arguments[0].click();", next_button)
                
                # Wait for the page to load
                print("Waiting for next page to load...")
                random_sleep(8, 12)
                
                # Check if Cloudflare interrupt happened
                if "Just a moment" in driver.title:
                    print("Detected Cloudflare challenge. Please solve it manually if needed.")
                    # Give user time to solve CAPTCHA if it appears
                    time.sleep(20)
                
                page_count += 1
                
            except Exception as e:
                print(f"Error navigating to next page: {e}")
                print("Trying alternative method...")
                
                try:
                    # Try direct URL navigation to next page
                    if "page/" in current_url:
                        # Extract current page number
                        parts = current_url.split("page/")
                        current_page_num = int(parts[1].split("/")[0])
                        next_page_num = current_page_num + 1
                        next_url = f"{parts[0]}page/{next_page_num}/"
                    else:
                        # If first page doesn't have page number in URL
                        next_url = f"{current_url}page/2/"
                        
                    print(f"Navigating directly to: {next_url}")
                    driver.get(next_url)
                    random_sleep(8, 12)
                    page_count += 1
                except Exception as nav_error:
                    print(f"Failed to navigate to next page: {nav_error}")
                    print("Saving checkpoint before exiting...")
                    save_checkpoint(page_count, scraped_data, current_url)
                    break
    
    except KeyboardInterrupt:
        print("\nScraping interrupted by user. Saving checkpoint...")
        save_checkpoint(page_count, scraped_data, driver.current_url)
    
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Saving checkpoint before exiting...")
        try:
            save_checkpoint(page_count, scraped_data, driver.current_url)
        except:
            # In case driver is not accessible
            save_checkpoint(page_count, scraped_data, start_url)
    
    finally:
        # Save the final results
        if scraped_data:
            df = pd.DataFrame(scraped_data, columns=['Title', 'Author', 'Date', 'Excerpt'])
            df.to_csv('businessday_final3.csv', index=False)
            print(f"\nScraping completed. Saved {len(scraped_data)} articles to businessday_final.csv")
        else:
            print("No data was scraped")
            
        # Close the browser
        driver.quit()

if __name__ == "__main__":
    main()