from selenium import webdriver
from selenium.webdriver.chrome.options import Options # Cleaner logging
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import csv
from datetime import datetime
import re

"""
Run first
Outputs "voedingscentrum_recipes.csv"
"""

MAIN_URL = 'https://www.voedingscentrum.nl/nl/zoek.aspx?categorie=recept'
todays_date = datetime.today().strftime('%Y-%m-%d')

def get_full_page_html(url, max_wait_time=40): # this is how long to scroll the page to load recipes
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # Scroll the page to load recipes
    last_height = driver.execute_script("return document.body.scrollHeight")
    start_time = time.time()

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.4) # Pause scroll to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break # Stop if reached the end of it all
        last_height = new_height
        if time.time() - start_time > max_wait_time:
            print("Reached scroll timeout.")
            break

    html = driver.page_source
    driver.quit()
    return html

def extract_numeric_value(text):
    """
    Extracts the first numeric value from a string, allowing for decimal points.
    Returns it as a float if possible, or an empty string if not found.
    """
    if pd.isna(text):
        return ''
    match = re.search(r'[\d]+(?:[.,]\d+)?', str(text))
    if match:
        value = match.group(0).replace(',', '.')
        try:
            return float(value)
        except ValueError:
            return ''
    return ''

def extract_all_links(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a', class_='sr-link')
    recipes = [] # Empty list for disctionaries

    for link in links:
        href = link.get('href')
        title = link.get('title')
        if href and title:
            full_url = urljoin(base_url, href)
            recipes.append({'title': title.strip(), 'url': full_url})
    return recipes

import csv  # Required for quoting in CSV

def extract_recipe_details(url):
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(3)

    html = driver.page_source
    driver.quit()
    soup = BeautifulSoup(html, 'html.parser')

    # Skip non-vegetarian
    if not soup.select_one('li.vegetarisch'):
        return None

    # Title
    title = soup.find('h1').get_text(strip=True) if soup.find('h1') else ''

    # Ingredients
    ingredients = soup.select('div.ingredienten div.columns.group ul li')
    ingredients = [li.get_text(strip=True) for li in ingredients]

    # Category (ontbijt, lunch, etc.)
    category = soup.select_one('li.gerecht')
    category = category.get_text(strip=True) if category else ''

    # Servings] size
    servings = soup.select_one('li.personen')
    servings = servings.get_text(strip=True) if servings else ''

    # Nutrition table extraction

    def extract_nutrition(prop):
        tag = soup.select_one(f'td[itemprop="{prop}"]')
        if not tag:
            return ''
        raw = tag.get_text(separator=' ', strip=True)
        cleaned = re.sub(r'\s+', ' ', raw)  # Collapse all whitespace
        cleaned = cleaned.replace(',', '.')  # Convert 0,5 --> 0.5
        return cleaned


    kcal       = extract_nutrition("calories")
    vet        = extract_nutrition("fatContent")
    vet_verz   = extract_nutrition("saturatedFatContent")
    koolhydr   = extract_nutrition("carbohydrateContent")
    suikers    = extract_nutrition("sugarContent")
    vezels     = extract_nutrition("fiberContent")
    eiwit      = extract_nutrition("proteinContent")
    zout       = extract_nutrition("sodiumContent")

    return {
        'title': title,
        'url': url,
        'ingredients': ', '.join(ingredients),
        'category': category,
        'servings': servings,
        'kcal': extract_numeric_value(kcal),
        'vet': extract_numeric_value(vet),
        'verzadigd_vet': extract_numeric_value(vet_verz),
        'koolhydraten': extract_numeric_value(koolhydr),
        'suikers': extract_numeric_value(suikers),
        'vezels': extract_numeric_value(vezels),
        'eiwit': extract_numeric_value(eiwit),
        'zout': extract_numeric_value(zout),
        'datum': todays_date
}

# ------------------ Run ------------------------

print("Scrolling and extracting all recipe links...")
page_html = get_full_page_html(MAIN_URL)
recipe_links = extract_all_links(page_html, MAIN_URL)
print(f"Found {len(recipe_links)} recipes")

all_data = []
# 2.5 minutes for 20 recipes
for i, recipe in enumerate(recipe_links[:20]): # this is how many recipes to collect before being satisfied
    print(f"[{i+1}/{len(recipe_links)}] Scraping: {recipe['title']}")
    try:
        details = extract_recipe_details(recipe['url'])
        if details:
            all_data.append(details)
        else:
            print(f"Skipped (not vegetarian): {recipe['title']}")
    except Exception as e:
        print(f"Failed to scrape {recipe['url']}: {e}")


# ------------------ Save to CSV ------------------

df = pd.DataFrame(all_data)
df.to_csv("voedingscentrum_recipes.csv", index=False, encoding='utf-8-sig', quoting=csv.QUOTE_ALL)
print("Saved all recipes to voedingscentrum_recipes.csv")
