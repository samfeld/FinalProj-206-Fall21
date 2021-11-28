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
    """
    This function creates the database titled 'Meals2.db' that will be referenced.
    It returns the connection to the database and the cursor.
    """
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def setUpIngredientsTable(data, cur, conn):
    """
    This function creates the table Ingredients in the database.
    The table has 2 columns: id and Ingredient. 
    The id is autoincremented and the Ingredients are taken from
    a list of all of the ingredients on the 'themealdb.com'. 
    This function does not return anything 
    """
    ingredient_lst = []
    for meal in data['meals']:
        id=meal["idIngredient"]
        ingredient = meal['strIngredient']
        if ingredient not in ingredient_lst:
            ingredient_lst.append(ingredient)
    cur.execute("CREATE TABLE IF NOT EXISTS Ingredients (id INTEGER PRIMARY KEY NOT NULL, Ingredient TEXT)")
    for i in range(len(ingredient_lst)):
        cur.execute("INSERT OR IGNORE INTO Ingredients (id,Ingredient) VALUES (?,?)",(i ,ingredient_lst[i]))
    conn.commit()

def find_meals(main_ingredient):
    """
    This function takes a main ingredient (e.g Chicken, Avocado).
    It the calls TheMealDB API to get meals whose main ingredient is the one provided.
    It returns the value as a list of dictionaries with information about the meals 
    """
    base_url="https://www.themealdb.com/api/json/v1/1/filter.php?i={}"
    request_url=base_url.format(main_ingredient)
    data=requests.get(request_url)
    data2=data.text
    dict_list=json.loads(data2)
    return dict_list


def create_meals_tables(cur, conn):
    """
    This function creates the table Meals in the database.
    It does not return anything. 
    """
    cur.execute("CREATE TABLE IF NOT EXISTS Meals (key INTEGER PRIMARY KEY, Main_ingredient_id INTEGER, Meal TEXT UNIQUE)")
    conn.commit()


def update_meals_table(cur, conn):
    """
    This function updates the Meals table.
    It calls the find_meals function on each of the ingredients in the Ingredients table. 
    It then adds the meals to the table with a specification of which main ingredient is used, with the Main_ingredient_id.
    This function does not return anything.
    """
    ids_in_table=[]
    cur.execute("SELECT COUNT(*) FROM Meals")
    count_meals=int(cur.fetchone()[0])
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


def num_meals_for_ingredient(cur, conn):
    """
    This function counts the number of meals each ingredient is the main ingredient for.
    It returns a list of tuples, each of which contains the ingredient and the count of meals it is the main ingredient for.
    This function calls on both tables Ingredients and Meals and joins them in order to retrieve this information.

    """
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
        tup=(current_ingr,current_count)
        ingredients_meal_count.append(tup)
        conn.commit()
        count+=current_count
    return ingredients_meal_count

def write_csv(tup, filename):
    """
    This function takes in a tuples (called tup, i.e. the
    one that is returned after running the num_meals_for_ingredients() function
    and then sorting the list to find the highest and lowest meal counts, 
    writes the data to a csv file, and saves it to the passed filename.
    This function does not return anything. 
    """
    with open(filename, "w", newline="") as fileout:
        header=["Ingredient with most meals","Ingredient with least meals"]
        writer=csv.writer(fileout)
        writer.writerow(header)
        writer.writerow(tup)


def main():
    """
    This function first sets up the database, which is named Meals2.db.
    It then created the Ingredients table, accessing the Meals DB API.
    """
    cur, conn = setUpDatabase('Meals2.db')
    lst_ingredients=requests.get("https://www.themealdb.com/api/json/v1/1/list.php?i=list").text
    ingredient_data=json.loads(lst_ingredients)
    setUpIngredientsTable(ingredient_data, cur, conn)

    create_meals_tables(cur, conn)
    update_meals_table(cur, conn)


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
    
    #visualization below:
    count_meals=num_meals_for_ingredient(cur, conn)
    
    ingredients=[]
    counts_of_meals=[]
    for count in count_meals:
        ingredients.append(count[0])
        counts_of_meals.append(count[1])
    
    #colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue']
    #explode = (0.1, 0, 0, 0)  # explode 1st slice
 
# Plot
    plt.pie(counts_of_meals, labels=ingredients, 
        autopct='%1.1f%%', shadow=True, startangle=140)
 
    plt.axis('equal')
    plt.show()

if __name__ == "__main__":
    main()
