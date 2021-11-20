import sqlite3
import json
import os
import requests
import unittest
import random
import matplotlib.pyplot as plt
import csv

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
    #cur.execute("DROP TABLE IF EXISTS Ingredients")
    cur.execute("CREATE TABLE IF NOT EXISTS Ingredients (id INTEGER PRIMARY KEY NOT NULL, Ingredient TEXT)")
    for i in range(len(ingredient_lst)):
    #for i in range(limit):
        cur.execute("INSERT OR IGNORE INTO Ingredients (id,Ingredient) VALUES (?,?)",(i ,ingredient_lst[i]))
    conn.commit()

def find_meals(main_ingredient):
    base_url="https://www.themealdb.com/api/json/v1/1/filter.php?i={}"
    request_url=base_url.format(main_ingredient)
    data=requests.get(request_url)
    data2=data.text
    dict_list=json.loads(data2)
    return dict_list


def create_meals_tables(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Meals (key INTEGER PRIMARY KEY, Main_ingredient_id INTEGER, Meal TEXT UNIQUE)")
    conn.commit()


def update_meals_table(cur, conn):
    ids_in_table=[]
    cur.execute("SELECT COUNT(*) FROM Meals")
    count_meals=int(cur.fetchone()[0])
    #if count_meals>0:
    #    for c in range(count_meals):
     #       cur.execute("SELECT Main_ingredient_id FROM Meals WHERE key={}".format(c))
      #      current_key=cur.fetchone()[0]
            #ids_in_table.append(current_key)
    key=1
    cur.execute("SELECT COUNT(key) FROM MEALS")
    last_key=cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM Ingredients")
    count_ingredients=int(cur.fetchone()[0])
    while key <26:
        target_id=random.randint(0, count_ingredients-1)
        if target_id not in ids_in_table:
            #print(target_id)
            cur.execute("SELECT Ingredient FROM Ingredients WHERE id={}".format(target_id))
            ingredient=cur.fetchone()[0]
            meal_data=find_meals(ingredient)
            ids_in_table.append(target_id)
            try: 
                for meal in meal_data["meals"]:
                    if key<26:
                        if meal['strMeal']!=None:
                #meal_name=meal_data["meals"][key]['strMeal']
                            meal_name=meal['strMeal']
                            cur.execute("INSERT INTO Meals (key, Main_ingredient_id, Meal) VALUES (?,?,?) ", (last_key+key, target_id, meal_name))
                            conn.commit()
                            key+=1
                            #print(key)
                        else:
                            continue
                    else:
                        break
            except:
                continue
        else:
            continue
            
    conn.commit()

"""def num_meals_for_ingredient(cur, conn, ingredient):
    cur.execute("SELECT COUNT(Meal) FROM Meals m JOIN Ingredients i ON m.Main_ingredient_id=i.id WHERE i.Ingredient={}".format(ingredient))
    current_count=cur.fetchone()[0]
    conn.commit()
    tup=(ingredient, current_count)
    return tup"""
        
def num_meals_for_ingredient(cur, conn):
    cur.execute("SELECT COUNT(*) From Meals")
    num_ingredients_listed=cur.fetchone()[0]
    count=1
    #for x in range(count):
    ingredients_meal_count=[]
    while count<num_ingredients_listed:
        cur.execute("SELECT Main_ingredient_id FROM Meals WHERE key={}".format(count))
        current_id=cur.fetchone()[0]
        print(current_id)
        #cur.execute("SELECT Main_ingredient_id FROM Meals WHERE key={}".format(count))
        cur.execute("SELECT i.Ingredient FROM Ingredients i JOIN Meals m ON m.Main_ingredient_id=i.id WHERE m.Main_Ingredient_id={}".format(current_id))
        current_ingr=cur.fetchone()[0]
        #cur.execute("SELECT i.id FROM Ingredients i JOIN Meals m ON m.Main_ingredient_id=i.id WHERE m.key={}".format(count))
        #current_id=cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM Meals WHERE Main_ingredient_id={}".format(current_id))
        current_count=cur.fetchone()[0]
        #for i in range(current_count):
        tup=(current_ingr,current_count)
        ingredients_meal_count.append(tup)
        #current_id=cur.fetchone()[0]
        #cur.execute("SELECT COUNT(*) From Meals m JOIN Ingredients i ON m.Main_ingredient_id=i.id WHERE m.Main_ingredient_id={}".format(current_id))
    #cur.execute("SELECT COUNT(*) From Meals m JOIN Ingredients i ON m.Main_ingredient_id=i.id WHERE m.Main_ingredient_id=0")
        conn.commit()
        count+=current_count
    #print(count)
    return ingredients_meal_count

def write_csv(tup, filename):
    with open(filename, "w", newline="") as fileout:
        header=["Ingredient with most meals","Ingredient with least meals"]
        writer=csv.writer(fileout)
        writer.writerow(header)
        writer.writerow(tup)


def main():
    # SETUP DATABASE AND TABLE
    cur, conn = setUpDatabase('Meals2.db')
    lst_ingredients=requests.get("https://www.themealdb.com/api/json/v1/1/list.php?i=list").text
    ingredient_data=json.loads(lst_ingredients)
    setUpIngredientsTable(ingredient_data, cur, conn)

    create_meals_tables(cur, conn)
    update_meals_table(cur, conn)
    """cur.execute("SELECT COUNT(DISTINCT Main_ingredient_id) FROM Meals")
    counts_meals=[]
    num_of_ingredients_listed=cur.fetchone()[0]
    i=1
    while i<num_of_ingredients_listed:
        cur.execute("SELECT Main_ingredient_id FROM Meals WHERE key={}".format(i))
        id=cur.fetchone()[0]
        cur.execute("SELECT COUNT(Meal) FROM Meals WHERE Main_ingredient_id={}".format(id))
        increment_by=cur.fetchone()[0]
        cur.execute("SELECT Ingredient FROM Ingredients WHERE id={}".format(id))
        ingr=cur.fetchone()[0]
        count_tup=num_meals_for_ingredient(cur, conn, ingr)
        counts_meals.append(count_tup)
        i+=increment_by
    sorted_by_count=sorted(counts_meals, key=lambda x:x[1], reverse=True)
    ingredient_most_meals=sorted_by_count[0][0]
    print(ingredient_most_meals)"""

    count_meals=num_meals_for_ingredient(cur, conn)
    print(count_meals)
    sorted_by_count=sorted(count_meals, key=lambda x:x[1], reverse=True)
    print(sorted_by_count)
    ingredient_most_meals=sorted_by_count[0][0]
    sorted_least=sorted(count_meals, key=lambda x:x[1])
    ingredient_least_meals=sorted_least[0][0]
    print(ingredient_most_meals)
    update_meals_table(cur, conn)
    calculations=(ingredient_most_meals, ingredient_least_meals)
    write_csv(calculations, "Meals_Calcultions.txt")
    
    
    
    

if __name__ == "__main__":
    main()
