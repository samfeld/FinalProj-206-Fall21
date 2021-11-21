import csv
import matplotlib.pyplot as plt
import sqlite3
import unittest
import os

path = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(path+'/'+"Meals2.db")
cur = conn.cursor()

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
    one that is returned by CALCULATION FUNCTION ADD HERE, 
    writes the data to a csv file, and saves it to the passed filename.
    This function does not return anything. 
    """
    with open(filename, "w", newline="") as fileout:
        header=["Ingredient with most meals","Ingredient with least meals"]
        writer=csv.writer(fileout)
        writer.writerow(header)
        writer.writerow(tup)


count_meals=num_meals_for_ingredient(cur, conn)
print(count_meals)
sorted_by_count=sorted(count_meals, key=lambda x:x[1], reverse=True)
print(sorted_by_count)
ingredient_most_meals=sorted_by_count[0][0]
sorted_least=sorted(count_meals, key=lambda x:x[1])
ingredient_least_meals=sorted_least[0][0]
print(ingredient_most_meals)
calculations=(ingredient_most_meals, ingredient_least_meals)
write_csv(calculations, "Meals_Calcultions.txt")
    
#visualization below:
count_meals=num_meals_for_ingredient(cur, conn)
    
ingredients=[]
counts_of_meals=[]
for count in count_meals:
    ingredients.append(count[0])
    counts_of_meals.append(count[1])
 
# Plot
    plt.pie(counts_of_meals, labels=ingredients, 
        autopct='%1.1f%%', shadow=True, startangle=140)
 
    plt.axis('equal')
    plt.show()
