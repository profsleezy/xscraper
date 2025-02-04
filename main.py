from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import re
from datetime import datetime, timezone, timedelta
import sys

# Configuration
X_URL = "https://twitter.com/login"
USERNAME = ""
PASSWORD = ""
EMAILORNUM = ""

# Generate dynamic date (one day before today)
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# Construct search URL with dynamic date
SEARCH_URL = f"https://x.com/search?q=launch%2C%20solana%20%2C%20pump%20fun%20(launch%2C%20OR%20solana%20OR%20%2C%20OR%20pump%20OR%20fun%2C%20OR%20pumpdotfun%2C%20OR%20meme%20OR%20coin%2C%20OR%20meme%2C%20OR%20coin%2C%20OR%20token%2C%20OR%20crypto%2C%20OR%20presale)%20since%3A{yesterday}%20-filter%3Areplies&src=typed_query&f=top"

# Function to start a new browser session
def start_new_browser_session():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    service = Service('chromedriver')

    # Start the browser
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# Start a new session
driver = start_new_browser_session()

try:
    print("[INFO] Opening login page...")
    driver.get(X_URL)
    wait = WebDriverWait(driver, 10)

    # Enter username
    username_field = wait.until(EC.presence_of_element_located((By.NAME, "text")))
    username_field.send_keys(USERNAME)
    username_field.send_keys(Keys.RETURN)
    time.sleep(2)

    # Handle verification prompt if it appears
    try:
        verification_prompt = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='text']")))
        verification_prompt.send_keys(EMAIL)
        verification_prompt.send_keys(Keys.RETURN)
        time.sleep(2)
    except:
        pass  # No verification prompt

    # Enter password
    password_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))
    password_field.send_keys(PASSWORD)
    password_field.send_keys(Keys.RETURN)

    # Wait for homepage
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='AppTabBar_Home_Link']")))
    print("[SUCCESS] Login successful!")

    # Go to search page
    driver.get(SEARCH_URL)
    print(f"[INFO] Opening search URL: {SEARCH_URL}")
    time.sleep(5)

    seen_posts = set()
    last_tweet_time = datetime.now(timezone.utc)  # Track latest tweet timestamp
    scroll_count = 0  # Track number of scrolls
    last_refresh_time = datetime.now(timezone.utc)  # Track the last refresh time

    while True:
        posts = driver.find_elements(By.CSS_SELECTOR, "article")
        new_posts_found = False  # Flag to check if we get new tweets

        for post in posts:
            try:
                # Extract tweet text
                text = post.text.strip()
                if not text or text in seen_posts:
                    continue  # Skip duplicate or empty tweets

                # Extract timestamp
                try:
                    timestamp_element = post.find_element(By.CSS_SELECTOR, "time")
                    tweet_time = timestamp_element.get_attribute("datetime")
                    tweet_datetime = datetime.fromisoformat(tweet_time[:-1]).replace(tzinfo=timezone.utc)  # Convert to UTC
                except:
                    continue  # Skip if no timestamp

                # Compare with current time
                current_time = datetime.now(timezone.utc)
                time_diff = (current_time - tweet_datetime).total_seconds() / 60  # Difference in minutes

                if time_diff > 3:
                    continue  # Skip if tweet is older than 3 minutes

                # Extract account link
                try:
                    account_element = post.find_element(By.CSS_SELECTOR, "a[href*='/']")
                    account_url = account_element.get_attribute("href")
                except:
                    continue  # Skip if no account link

                # Open profile in new tab
                driver.execute_script("window.open(arguments[0], '_blank');", account_url)
                WebDriverWait(driver, 5).until(lambda d: len(d.window_handles) > 1)

                # Switch to new tab
                driver.switch_to.window(driver.window_handles[-1])
                time.sleep(3)

                # Get followers count
                followers_count = 0
                try:
                    followers_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'followers')]//span"))
                    )
                    followers_text = followers_element.text.replace(",", "").replace(".", "")
                    match = re.search(r'\d+', followers_text)
                    if match:
                        followers_count = int(match.group())
                except:
                    followers_count = 0  # Default to 0 if error occurs

                # Close profile tab before filtering to avoid unnecessary browser usage
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                # ✅ Only log if followers are 1K+ and tweet is less than 3 minutes old
                if followers_count >= 1000:
                    print("=" * 50)
                    print(f"✅ Account: {account_url} ({followers_count} Followers)")
                    print(f"⏰ Tweet Time: {tweet_datetime.strftime('%Y-%m-%d %H:%M:%S UTC')}")
                    print(f"📢 Tweet: {text}")
                    print("=" * 50)

                    seen_posts.add(text)  # Add the text of this tweet to the seen set
                    last_tweet_time = tweet_datetime  # Update last tweet timestamp
                    new_posts_found = True  # Mark that we got new tweets

            except:
                continue  # Skip tweet if any unexpected error occurs

        # Reset seen_posts after refresh (to not miss any new post)
        if not new_posts_found:
            time_since_last_tweet = (datetime.now(timezone.utc) - last_tweet_time).total_seconds() / 60
            if time_since_last_tweet > 2:
                print("[INFO] No new tweets found, refreshing page...")
                current_time = datetime.now(timezone.utc)
                # Ensure refresh is at least 2 minutes apart
                if (current_time - last_refresh_time).total_seconds() >= 120:
                    driver.refresh()
                    last_refresh_time = current_time  # Update last refresh time
                    time.sleep(5)  # Wait after refresh
                    seen_posts.clear()  # Reset seen posts after refresh
                else:
                    print("[INFO] Refresh skipped: Less than 2 minutes since last refresh.")

        # Scroll down for more tweets
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        scroll_count += 1

        # Refresh after every 3 scrolls, ensuring 2 minutes between refreshes
        if scroll_count >= 3:
            print("[INFO] Scrolled 3 times, checking if refresh is possible...")
            current_time = datetime.now(timezone.utc)
            if (current_time - last_refresh_time).total_seconds() >= 120:
                print("[INFO] Refreshing page after 3 scrolls...")
                driver.refresh()
                last_refresh_time = current_time  # Update last refresh time
                time.sleep(5)  # Wait after refresh
                seen_posts.clear()  # Reset seen posts after refresh
                scroll_count = 0  # Reset scroll count
            else:
                print("[INFO] Refresh skipped: Less than 2 minutes since last refresh.")

finally:
    driver.quit()
