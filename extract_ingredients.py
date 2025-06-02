import pandas as pd
import re
from collections import Counter
import os.path

"""
Run third
Outputs: cleaned_ingredients.csv
"""

# Load CSV file
if os.file.ispath("./voedingscentrum_recipes_klimaat.csv"):
    df = pd.read_csv("voedingscentrum_recipes_klimaat.csv")
else:
    df = pd.read_csv("voedingscentrum_recipes.csv")

# If key is in the ingredient, use the value (so sunflower oil, olive oil, etc are all oil)
synonyms = {
    'olie': 'olie',
    'yoghurt': 'yoghurt',
    'knoflookteen': 'knoflook',
    'bosuien': 'bosui',
    'margarine': 'boter',
    'blauwe bessen': 'blauwe bessen',
    'bramen': 'bramen',
    'frambozen': 'frambozen',
    'bana': 'bananen',
    'kaas': 'kaas',
    }

def generalize_ingredient(name):
    for key, value in synonyms.items():
        if key in name:
            return value
    return name.strip().lower()

def extract_ingredient_names(ingredient_string):
    entries = [e.strip() for e in ingredient_string.split(',')]
    simplified = []

    for entry in entries:
        entry = entry.lower()
        entry = re.sub(r'\d+[.,]?\d*\s*(gram|ml|stukje|kneepje|stukjes|eetlepel|eetlepels|theelepel|theelepels|stukken?|snufje|teentje|teentjes|middelgrote|takjes|plakken?|bosjes?|blaadjes?|personen?)\s*', '', entry, flags=re.IGNORECASE)
        entry = re.sub(r'\b\d+[.,]?\d*\b', '', entry)
        entry = re.sub(r'\(.*?\)', '', entry)
        entry = re.sub(r"^\s*('s|'n|'t|de|het|een)\s+", '', entry)
        entry = re.sub(r'[¼½¾⅓⅔⅛⅜⅝⅞+§©®™†‡]', '', entry)
        entry = entry.strip(" ,.;:-")

        if entry:
            simplified.append(generalize_ingredient(entry))

    return simplified

def extract_numeric_value(text):
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

# Build new column for cleaned ingredients
ingredient_counter = Counter()
ingredients_cleaned_list = []

for _, row in df.iterrows():
    raw = row['ingredients']
    extracted = extract_ingredient_names(raw)
    ingredient_counter.update(extracted)
    ingredients_cleaned_list.append(', '.join(extracted))

# Add the new column to the existing DataFrame
df['ingredients'] = ingredients_cleaned_list

# Clean numerical nutrition fields in the DataFrame
columns_to_clean = ['kcal', 'vet', 'verzadigd_vet', 'koolhydraten', 'suikers', 'vezels', 'eiwit', 'zout', 'datum']
for col in columns_to_clean:
    if col in df.columns:
        df[col] = df[col].apply(extract_numeric_value)

output_df = df[['title', 'url', 'ingredients']]

# Overwrite the original CSV file with updated data
output_df.to_csv("grocery_ingredients.csv", index=False, encoding='utf-8-sig', quoting=1)
print("Saved to grocery_ingredients.csv.")
