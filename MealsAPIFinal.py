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
    It takes in 3 arguments: data (such as the ingredients list retrieved from the API),
    the database cursor, and database connection object.  
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
    It takes in 2 arguments: the database cursor, and database connection object.
    It does not return anything. 
    """
    cur.execute("CREATE TABLE IF NOT EXISTS Meals (key INTEGER PRIMARY KEY, Main_ingredient_id INTEGER, Meal TEXT UNIQUE)")
    conn.commit()


def update_meals_table(cur, conn):
    """
    This function updates the Meals table. It takes in 2 arguments: 
    the database cursor, and database connection object.
    It calls the find_meals function on each of the ingredients in the Ingredients table. 
    It then adds the meals to the table with a specification of which main ingredient is used, 
    with the Main_ingredient_id. This function does not return anything.
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
    This function takes in two arguments:
    the database cursor, and database connection object.
    It then counts the number of meals each ingredient is the main ingredient for.
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

def top_ten(lst_tups):
    """
    This function takes in a list of tuples (called lst_tups, i.e. the
    one that is returned after running the num_meals_for_ingredients() function).
    The function then sorts this list.
    It returns the 10 Ingredients with the most meals.
    If there are 10 or more meals in the database, it will return the top 10.
    Otherwise (if, for example, 25 meals are added to the database but many share 
    the same main ingredient and therefore 10 have not been added yet), the function
    will return the ingredients that are currently in the database. """
    lst_tups=sorted(lst_tups, key=lambda x: x[1], reverse=True)
    if len(lst_tups)>=10:
        lst_top_10=lst_tups[0:10]
    else:
        lst_top_10=lst_tups
    print(lst_top_10)
    return lst_top_10

def write_csv(tup, top_10, filename):
    """
    This function takes in a tuple, a list tuples, and a filename.
    The tuple should contain the ingredient with the most meals, followed by the
    ingredient with the least. The list of tuples is called top_10 (i.e. the
    one that is returned after running the lst_top_10() function) contains the 
    10 Ingredients with the highest number of meals. 
    The function first writes a title for the file.
    It then writes the tuple of the ingredients with the highest and lowest counts of meals.
    Finally, it writes the Top 10 Ingredients along with their counts of meals. 
    This data is all written to a csv file, and saves it to the passed filename.
    This function does not return anything. 
    """
    with open(filename, "w", newline="") as fileout:
        writer=csv.writer(fileout)
        title=["Calculations from The Meals DB API"]
        writer.writerow(title)
        header1=["Ingredient with most meals","Ingredient with least meals"]
        writer.writerow(header1)
        writer.writerow(tup)
        writer.writerow("")
        header2=["Top 10 Main Ingredients Based Off Of Counts Of Meals:"]
        writer.writerow(header2)
        header3=["Ingredient", "Count of Meals With That Main Ingredient"]
        writer.writerow(header3)
        for tup in top_10:
            data=tup[0],tup[1]
            print(data)
            writer.writerow(data)


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
    sorted_by_count=sorted(count_meals, key=lambda x:x[1], reverse=True)
    #print(sorted_by_count)
    ingredient_most_meals=sorted_by_count[0][0]
    sorted_least=sorted(count_meals, key=lambda x:x[1])
    ingredient_least_meals=sorted_least[0][0]
    #print(ingredient_most_meals)
    update_meals_table(cur, conn)
    calculations=(ingredient_most_meals, ingredient_least_meals)
    calculated_top=top_ten(count_meals)
    write_csv(calculations, calculated_top, "Meals_Calcultions.txt")
    
    #visualization below:
    #count_meals=num_meals_for_ingredient(cur, conn)
    
    ingredients=[]
    counts_of_meals=[]
    for count in sorted_by_count:
        ingredients.append(count[0])
        counts_of_meals.append(count[1])

 
# The code below creates a Pie Chart of the ingredients and their meal counts.
#
    colors=["magenta", "cyan", "orange", "yellow", "violet", "red", "yellowgreen", "blue", "gold", "lightskyblue"]
    patches, labels, pct_texts=plt.pie(counts_of_meals[0:10], labels=ingredients[0:10], colors=colors,
        autopct='%1.1f%%', shadow=False, rotatelabels=True, startangle=140)
    for label, pct_text in zip(labels, pct_texts):
        pct_text.set_rotation(label.get_rotation())
    #sort_legend=True
    #if sort_legend:
    ##    patches, labels, dummy=zip(*sorted(zip(patches, labels, counts_of_meals), 
    #    key=lambda x: x[2],
    #    reverse=True))
    
    #labels = ['%s, %1.1f ' % (l, s) for l, s in zip(ingredients,counts_of_meals)] 
    plt.axis('equal')
    plt.title("Top 10 Main Ingredients For Meals", loc="right")
    #plt.legend(labels, loc="lower left", fontsize=8)
    #plt.legend(ingredients, loc="lower left", fontsize=8)
    plt.tight_layout()
    plt.show()
    #add title

if __name__ == "__main__":
    main()
