import csv
import sqlite3
import datetime
import random
import os

twitch_user = os.getenv("twitchuser") #Gets twitch username of who redeemed the hunt
hunt_type = os.getenv("hunttype", "Bugs")  #Gets type of hunt (fish, bug, plant, magical)

# Get the directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "pond_collection.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get the directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

#Makes tables for each type
def make_tables():
    for type in ['Bugs', 'Fish', 'Plants']:
        create_query = f"""CREATE TABLE IF NOT EXISTS {type}(
                            id INTEGER PRIMARY KEY,
                            name TEXT,
                            rarity TEXT,
                            season TEXT);"""
        cursor.execute(create_query)

#Insert values using preloaded csv files
def insert_values(csv_name):
    table_name = csv_name.removesuffix('.csv').capitalize()
    insert_query = f"""
                INSERT OR IGNORE INTO {table_name} (id, name, rarity, season)
                VALUES (?, ?, ?, ?);"""

    csv_path = os.path.join(SCRIPT_DIR, "data", csv_name)
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cursor.execute(insert_query
                , (int(row['id']), row['name'], row['rarity'], row['season']))
    conn.commit()

#Gets current season based on current month
def get_current_season():
    curr_time = datetime.datetime.now()
    month = curr_time.strftime("%B")
    match(month):
        case "March"|"April"|"May":
            curr_season = "Spring"
        case  "June"|"July"|"August":
            curr_season = "Summer"
        case "September"|"October"|"November":
            curr_season = "Fall"
        case "December"|"January"|"February":
            curr_season = "Winter"
    return curr_season

#Gets random item from tables using rarity weights
def get_random_item():
    curr_season = get_current_season()
    keys = ['id', 'name', 'rarity', 'season']
    sql_query = f"SELECT * FROM {hunt_type} WHERE season LIKE ?"
    cursor.execute(sql_query, (f"%{curr_season}%",)) #Selects all items that are collectable in this season
    results = cursor.fetchall()

    RARITY_WEIGHTS = {
        "common": 70,
        "uncommon": 20,
        "rare": 9,
        "legendary": 1
    }

    item_weights = [RARITY_WEIGHTS[item[2]] for item in results] #Assigns weight to each item that was returned from query
    item_tuple = random.choices(results, weights=item_weights, k=1)[0] #Selects a random item from possible items
    item_dict = dict(zip(keys, item_tuple)) #Reformats to dictionary with keys
    print(f"{item_dict['name']} was found!")
    return item_dict

#Adds to inventory table if item has not been discovered yet
def add_to_inventory(item):
    TIMESTAMP = datetime.datetime.now().strftime("%B %d, %Y") #Formats time as "January 01, 2000"
    cursor.execute("""CREATE TABLE IF NOT EXISTS Inventory(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        item_name TEXT,
                        item_type TEXT,
                        rarity TEXT,
                        discovered_on TEXT,
                        discovered_by TEXT);""")
    cursor.execute("SELECT * FROM Inventory WHERE item_name = ?", (item['name'],)) #Finds any instance of the item caught in existing inventory
    result = cursor.fetchone()

    #Adds to inventory if item was not found in inventory table
    if not result:
        print(f"You are the first to discover this {hunt_type.removesuffix('s').lower()}.")
        cursor.execute("""INSERT INTO Inventory(item_name, item_type, rarity, discovered_on, discovered_by)
                        VALUES (?, ?, ?, ?, ?)""", (item['name'], hunt_type.removesuffix('s').lower(), item['rarity'], TIMESTAMP, twitch_user))
        conn.commit()

def main():
    make_tables()
    insert_values("bugs.csv")
    insert_values("fish.csv")
    insert_values("plants.csv")
    hunted_item = get_random_item() #Starts hunt
    add_to_inventory(hunted_item) #Adds to community inventory

main()