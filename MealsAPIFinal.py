import sqlite3
import json
import os
import requests
import unittest

# Create Database
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def setUpIngredientsTable(data, cur, conn):
    ingredient_lst = []
    for meal in data['meals']:
        id=meal["idIngredient"]
        ingredient = meal['strIngredient']
        if ingredient not in ingredient_lst:
            ingredient_lst.append(ingredient)
    cur.execute("DROP TABLE IF EXISTS Ingredients")
    cur.execute("CREATE TABLE Ingredients (id INTEGER PRIMARY KEY NOT NULL, Ingredient TEXT)")
    for i in range(len(ingredient_lst)):
    #for i in range(limit):
        cur.execute("INSERT INTO Ingredients (id,Ingredient) VALUES (?,?)",(i ,ingredient_lst[i]))
    conn.commit()

def find_meals(main_ingredient):
    base_url="https://www.themealdb.com/api/json/v1/1/filter.php?i={}"
    request_url=base_url.format(main_ingredient)
    data=requests.get(request_url)
    data2=data.text
    dict_list=json.loads(data2)
    return dict_list


def create_meals_tables(cur, conn):
    count=0
    #cur.execute("CREATE TABLE AS (SELECT Ingredient FROM Ingredients WHERE Ingredient={})".format(ingredient))
    cur.execute("CREATE TABLE IF NOT EXISTS Meals (key INTEGER PRIMARY KEY, Main_ingredient_id INTEGER, Meal TEXT UNIQUE)")
    #cur.execute(f"CREATE TABLE {ingredient} (Main_ingredient_id INTEGER, Main_ingredient TEXT, Meal TEXT UNIQUE)")
    lst_meals=[]
    cur.execute("SELECT COUNT(*) FROM Ingredients")
    count_ingredients=int(cur.fetchone()[0])
    for i in range(count_ingredients):
 #for i in range(25):
        #cur.execute("SELECT Ingredient FROM Ingredients WHERE id={}".format(i))
        #should I use line below instead?
        cur.execute("SELECT Ingredient FROM Ingredients WHERE id={}".format(i))
        ingredient=cur.fetchone()[0]
        meal_data=find_meals(ingredient)
        try:
            #for meal in meal_data["meals"]:
            for i in range(25):
                meal_name=meal_data[i]['strMeal']
                cur.execute("SELECT COUNT key FROM MEALS")
                key=cur.fetchone()[0]+1
                print(key)
                cur.execute("INSERT OR IGNORE INTO Meals (key, Main_ingredient_id, Meal) VALUES (?,?,?) ", (key, i, meal_name))
                key+=1
                
        except:
            continue
    conn.commit()
    count+=25
def num_meals_for_ingredient(cur, conn, id):
    cur.execute("SELECT COUNT(*) From Meals m JOIN Ingredients i ON m.Main_ingredient_id=i.id WHERE m.Main_ingredient_id='{id}'")
    #cur.execute("SELECT COUNT(*) From Meals m JOIN Ingredients i ON m.Main_ingredient_id=i.id WHERE m.Main_ingredient_id=0")
    conn.commit()
    count=cur.fetchone()[0]
    #print(count)
    return count

def main():
    # SETUP DATABASE AND TABLE
    cur, conn = setUpDatabase('Meals2.db')
    lst_ingredients=requests.get("https://www.themealdb.com/api/json/v1/1/list.php?i=list").text
    ingredient_data=json.loads(lst_ingredients)
    #print(ingredient_data)
    limit=0
    #for i in range(4):
    #    limit+=25
    setUpIngredientsTable(ingredient_data, cur, conn)
    create_meals_tables(cur, conn)
    count_meals=[]
    print(num_meals_for_ingredient(cur, conn, 5))
    for i in range(len(ingredient_data["meals"])):
        current_count=num_meals_for_ingredient(cur, conn, i)
        tup=(ingredient_data["meals"][i]["strIngredient"], current_count)
        count_meals.append(tup)
    #print(count_meals)
    sorted_by_count=sorted(count_meals, key=lambda x:x[1])
    #print(sorted_by_count)

    
    
    
    

if __name__ == "__main__":
    main()
