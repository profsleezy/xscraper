# Twitter/X Crypto Tweet Scraper

## Overview
This Python script uses **Selenium** to automatically log into Twitter/X, search for recent tweets related to crypto launches, and filter them based on tweet age and follower count. The script scrolls and refreshes the page as needed to ensure it captures the latest tweets.

## Features
✅ **Automated Twitter/X Login** (requires credentials)  
✅ **Search for Crypto-Related Tweets** (dynamic date filtering)  
✅ **Filters Tweets:**  
   - Only logs tweets **less than 3 minutes old**  
   - Only logs tweets from accounts with **1,000+ followers**  
✅ **Scrolls & Refreshes Automatically** when no tweets are found  
✅ **Avoids Duplicate Processing**   

## Installation
### 1️⃣ Install Dependencies
Ensure you have Python installed, then install the required libraries:

```sh
pip install selenium
```

### 2️⃣ Download ChromeDriver
- This script requires **Google Chrome** and **ChromeDriver**.
- Download the correct version of ChromeDriver for your **Chrome version** from:  
  👉 [https://chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads)
- Place the `chromedriver` executable in the same folder as this script.

## Configuration
### 1️⃣ **Set Your Twitter/X Credentials**
Edit the following variables in the script:

```python
USERNAME = "your_twitter_username"
PASSWORD = "your_twitter_password"
EMAILORNUM = "your_email_or_phone_number"
```

### 2️⃣ **Adjust Search Filters**
The script **automatically searches for tweets from the last 24 hours**. If you want to change the keywords in the search query, modify this part:

```python
SEARCH_URL = f"https://x.com/search?q=launch%2C%20solana%20%2C%20pump%20fun%20(launch%2C%20OR%20solana%20OR%20%2C%20OR%20pump%20OR%20fun%2C%20OR%20pumpdotfun%2C%20OR%20meme%20OR%20coin%2C%20OR%20meme%2C%20OR%20coin%2C%20OR%20token%2C%20OR%20crypto%2C%20OR%20presale)%20since%3A{yesterday}%20-filter%3Areplies&src=typed_query&f=top"
```
- **To change keywords**, modify the part inside `q=...`.

### 3️⃣ **Modify Filtering Criteria**
- Change **minimum follower count** (default: `1,000`):
  ```python
  if followers_count >= 1000:
  ```
- Change **tweet freshness** (default: `3 minutes`):
  ```python
  if time_diff > 3:
  ```

### 4️⃣ **Adjust Scroll & Refresh Behavior**
- Change **maximum scrolls before refresh** (default: `3`):
  ```python
  if scroll_count >= 3:
  ```
- Change **minimum time between refreshes** (default: `2 minutes`):
  ```python
  if (current_time - last_refresh_time).total_seconds() >= 120:
  ```

## Running the Script
Run the script from the terminal:
```sh
python main.py
```

The script will log new tweets that meet the filtering criteria.

## Example Log Output
```
==================================================
✅ Account: https://x.com/SolanaSewer (6167 Followers)
⏰ Tweet Time: 2025-01-29 22:50:03 UTC
📢 Tweet: Automated EchoSpeak...
==================================================
[INFO] No new tweets found, refreshing page...
```

## Notes
- Make sure **ChromeDriver matches your Chrome version**.
- Twitter/X may update their site structure, which could require XPath/CSS selector updates.
- Running this script **violates Twitter/X's TOS**; use responsibly.

