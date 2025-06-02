# Final-Project

This project gather recipes from a website and generates a menu with constraints.

scrape_recipes.py: Run first. Scrapes recipes from the website voedingscentrum using webscraping techniques. Uses Selenium to load Java content and scroll the page for a select amount of time. Puts the recipe name with the link, as well as all nutritional information in a .csv for possible further working.

recepten_run_every_month.py: Run second. Uses the output file of the previous program. Want to be climate conscious this month? This program adds a climate conscious yes/no to each recipe. This is a separate program since this changes every month, and so you can run all the recipes in bulk just once, and only just this query once per month, or not.

extract_ingredients.py: Run third. Strips ingredients for the purpose of a future grocery shopping conscious menu.

generate_menu: Run fourth. Generates menu with constraints.