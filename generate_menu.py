import pandas as pd
import random
from collections import Counter
import os.path

"""
Run fourth, generate menu
"""

# ------------------------- Load and prepare the data

while True:
    try:
        klimaatvriendelijk_yn = str(input("Do you want only recipes that are klimaatvriendelijk this season? y/n: ")).strip().lower()
    except ValueError:
        continue
    if klimaatvriendelijk_yn == "y":
        klimaatvriendelijk_yn = "yes"
        break
    elif klimaatvriendelijk_yn == "n":
        klimaatvriendelijk_yn = "no"
        break

# Load CSV file. Filter on y if desired
if os.file.ispath("./voedingscentrum_recipes_klimaat.csv") and klimaatvriendelijk_yn == "yes":
    df = pd.read_csv("voedingscentrum_recipes_klimaat.csv")
    df = df[df["klimaatvriendelijk"] == klimaatvriendelijk_yn]
else:
    df = pd.read_csv("voedingscentrum_recipes.csv")

# ----------------- Pick 7 recipes with max 3 unique titles

def pick_7_recipes_max_3_unique(df_category):
    """
    Picks 7 recipes from the given category from the DataFrame,
    such that there are at most 3 unique titles (eg. AABBCCC)
    """
    for _ in range(1000):  # Try 1000 times
        sampled = df_category.sample(n=7, replace=True)  # Allow duplicates
        title_counts = Counter(sampled["title"])
        if len(title_counts) <= 3:
            return sampled
    return None  # Fail if no such combination is found

# ------- Generate a full menu that meets all constraints

for attempt in range(1000):
    # Filter data by category
    ontbijt_df = df[df["category"].str.contains("ontbijt", case=False, na=False)]
    lunch_df = df[df["category"].str.contains("lunch", case=False, na=False)]
    hoofdgerecht_df = df[df["category"].str.contains("hoofdgerecht", case=False, na=False)]

    # For each category, pick 7 recipes
    ontbijt = pick_7_recipes_max_3_unique(ontbijt_df)
    lunch = pick_7_recipes_max_3_unique(lunch_df)
    hoofdgerecht = pick_7_recipes_max_3_unique(hoofdgerecht_df)

    # If any category fails to meet the constraint, try again
    if ontbijt is None or lunch is None or hoofdgerecht is None:
        continue

    # Combine all 21 recipes
    full_menu = pd.concat([ontbijt, lunch, hoofdgerecht])

    # Check total nutrients across all recipes
    total_vezels = full_menu["vezels"].sum()
    total_protein = full_menu["eiwit"].sum()

    if total_vezels >= 200 and total_protein >= 200:
        print("Found menu!")
        print(full_menu[["title", "category", "vezels_num", "eiwit"]].to_string(index=False))
        print(f"\nTotal vezels: {total_vezels:.1f} g")
        print(f"Total eiwitten: {total_protein:.1f} g")
        break
else:
    print("No valid menu found after 1000 attempts.")
