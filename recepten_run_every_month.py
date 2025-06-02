import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests

"""
Run second
Outputs: voedingscentrum_recipes_klimaat.csv
"""
# Check if fast request first
def check_klimaat_requests(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        html = requests.get(url, headers=headers, timeout=5).text
        soup = BeautifulSoup(html, 'html.parser')
        span = soup.select_one('div.rz-recipe-infoblock span')
        if span:
            text = span.get_text(strip=True).lower()
            if "deze maand niet klimaatvriendelijk" in text or "geen klimaatvriendelijke keuze" in text:
                return "no"
            return "yes"
        return "unknown"
    except Exception:
        return None

# Load CSV file
df = pd.read_csv("voedingscentrum_recipes.csv")

# Load browser session (so that it doesn't open a new one for each recipe)
options = Options()
options.headless = True
driver = webdriver.Chrome(options=options)

# Add new column by checking each URL
klimaat_list = []
for i, row in df.iterrows():
    url = row["url"]
    print(f"[{i+1}/{len(df)}] Checking klimaatvriendelijk for: {row['title']}")

    # Check fast request:
    result = check_klimaat_requests(url)
    klimaat_list.append(result)

# Close browser session
driver.quit()

# Always override or insert the column
df.loc[:, "klimaatvriendelijk"] = klimaat_list

# Save to new CSV
df.to_csv("voedingscentrum_recipes_klimaat.csv", index=False, encoding='utf-8-sig', quoting=1)  # quoting=1 = QUOTE_ALL
print("Saved to voedingscentrum_recipes_klimaat.csv")
