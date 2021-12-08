from typing import ItemsView, List, Tuple
from bs4 import BeautifulSoup
import requests
import unittest
import sqlite3
import json
import os
import matplotlib
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import random
import csv

def setUpDatabase(db_name):
    """
    This function creates the database titled "college_cooks.db". 
    It returns the connection to the database and the cursor.
    """
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def get_data_from_website(url):
    """
    This function scrapes the data from the Top100 Diners website using 
    BeautifulSoup. It returns multiple lists of the names, the type, 
    the dollar signs (cost), the reviews, and the location for each restaurant. 
    """
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html.parser')
    name_tags = soup.find_all('h2')
    type_tags=soup.find_all('div', class_='overview__3pYsRoNl')
    review_tags=soup.find_all('div', class_='ratingReviews__33xaxtwo')
    location_tags=soup.find_all('div',class_='address__28bKEZcw')
    name_info = []
    type_info=[]
    money_info=[]
    review_info=[]
    location_info=[]
    for tag in name_tags:
        for sub_tag in tag:
            for tagg in sub_tag:
                name_info.append(tagg)
    for tag in type_tags:
        for sub_tag in tag:
            for tagg in sub_tag:
                if str(tagg)[0].isalpha():
                    type_info.append(tagg)
    for tag in type_tags:
        for sub_tag in tag:
            for tagg in sub_tag:
                if str(tagg).startswith('$'):
                    money_info.append(tagg)
    for tag in review_tags:
        for sub_tag in tag:
            for tagg in sub_tag:
                for taggg in tagg:
                    if str(taggg)[0].isdigit():
                        review_info.append(taggg)
    for tag in location_tags:
        for sub_tag in tag:
            for tagg in sub_tag:
                location_info.append(tagg)
    return name_info, type_info,  money_info,  review_info,  location_info


def create_table(cur,conn):
    """
    This function creates the restaurants table in the databse.
    It takes 2 arguments such as the database cursor, and database connection 
    object. It does not return anything. 
    """
    cur.execute("CREATE TABLE restaurants_table (id INTEGER PRIMARY KEY, name TEXT, type TEXT, money TEXT, review TEXT, location TEXT)")
def setup_restaurantstable(data, cur, conn):
    """
    This function puts the data into the restaurants_table. 
    It takes in 3 arguments such as data, which is the url of the website, 
    the database cursor, and the database connection object. 
    The table has 6 columns. They are id, restaurant name, type of restaurant,
    cost of restaurant (in $'s), number of reviews, and location.
    """
    id=0
    count=0
    final_list=[]
    for item in data:
        final_list.append(item)
    cur.execute("SELECT name FROM restaurants_table")
    names=cur.fetchall()
    name_list=[]
    for tup in names:
        name_list.append(tup[0])
    cur.execute("SELECT id FROM restaurants_table")
    ids=cur.fetchall()
    id_list=[]
    for tup in ids:
        id_list.append(int(tup[0]))
    try:
        id=max(id_list)
    except:
        id=0
        #create_table(cur, conn)
    while count <25:
        if id>=100:
            break
        for i in range(id,id+25):
            if final_list[0][i] not in name_list:
                name = final_list[0][i]
                type=final_list[1][i]
                money=final_list[2][i]
                review=final_list[3][i]
                location=final_list[4][i]
                id+=1
                count+=1
                cur.execute("INSERT OR IGNORE INTO restaurants_table (id, name, type, money, review, location) VALUES (?,?,?,?,?,?)",(id, name, type,money,review,location))    
        conn.commit() 
def calculate_average(cur, conn):
    """
    This function calculates the average number of dollar signs for each type of 
    restaurant. It takes in 2 arguments such as the database cursor and 
    the database connection object. It then wrties these averages in the 
    restaurant_calculations.txt file. The last section of this function creates 
    a visual using matplotlib to create a bar graph of these adverages. 
    """
    cur.execute("SELECT type, money FROM restaurants_table")
    info=cur.fetchall()
    count_dict={}
    total_dict={}
    average_dict={}
    for item in info:
        if item[0] not in count_dict:
            count_dict[item[0]]=1
        else:
            count_dict[item[0]]+=1
        if item[0] not in total_dict:
            total_dict[item[0]]=len(item[1])
        else:
            total_dict[item[0]]+=len(item[1])
    for type in count_dict:
        average_dict[type]=round(total_dict[type]/count_dict[type],2)
       
    with open('restaurant_calculations.txt', 'w') as f:
        for type in average_dict:
            if str(type).startswith('A') or str(type).startswith('E') or str(type).startswith('I') or str(type).startswith('O') or str(type).startswith('U') or str(type).startswith('Y'):
                f.writelines('The average cost of an ' + type + ' restaurant is ' + str(average_dict[type]) + " $'s.")
                f.write('\n')
            else:
                f.writelines('The average cost of a ' + type + ' restaurant is ' + str(average_dict[type]) + " $'s.")
                f.write('\n')
    f.close()


    fig=plt.figure(figsize=(16,8))
    matplotlib.rc('xtick', labelsize=6) 
    matplotlib.rc('ytick', labelsize=7)
    averages_list=[]
    names_list=[]
    for type in average_dict:
        names_list.append(type)
        averages_list.append(average_dict[type])
    plt.bar(names_list, averages_list, color=['midnightblue', 'mediumblue', 'blue', 'indigo', 'darkslateblue', 'royalblue', 'steelblue', 'dodgerblue', 'deepskyblue', 'lightskyblue', 'slateblue', 'mediumslateblue', 'purple', 'rebeccapurple', 'darkviolet', 'blueviolet', 'darkorchid', 'mediumpurple', 'mediumorchid', 'plum', 'violet', 'orchid', 'hotpink', 'lightpink', 'coral'], edgecolor='black')
    plt.xlabel('Type of Restaurant', fontweight='bold')
    plt.ylabel("Average $'s", fontweight='bold')
    plt.title("Average $'s for Type of Restaurant")
    plt.xticks(rotation=45)
    plt.show()

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
def getDishInfo():
    """
    This function accesses the Menus API from NYPL and extracts a list of dictionaries containing menu items and information pertaining to them.
    It uses the token that was given to us after requesting one.
    With the data extracted, the function then creates and returns a dictionary containing the dishes and the information.
    """
    url = 'http://api.menus.nypl.org/dishes?token='
    token = 'r6g4jg2ihzhad4xsjknj3lnr7u'
    request = requests.get(url + token, verify = False)
    data = request.json()
    data_dict = {}
    for d in data:
        data_dict[d] = data[d]
    return data_dict


def create_dish_table(cur, conn):
    """
    This function sets up the database with the dictionary returned by the getDishInfo function.
    It creates the table Dishes and, in increments of 25, inputs the dishes and a selection of data per dish.
    This function does not return anything, but rather inputs data into the database after each time it is run.
    Once run 4 times, all of the data from the data dictionary will be displayed on the database.
    """
    dish_dict = getDishInfo()
    cur.execute("CREATE TABLE IF NOT EXISTS Dishes (key INTEGER PRIMARY KEY, name TEXT UNIQUE, menus_appeared INTEGER, times_appeared INTEGER, first_appeared INTEGER, last_appeared INTEGER, lowest_price INTEGER, highest_price INTEGER)")
    key = 1
    cur.execute("SELECT COUNT(key) FROM DISHES")
    last_key = cur.fetchone()[0]
    while key < 26:
        for d in dish_dict['dishes']:
            if key < 26:
                name = d['name']
                menus_appeared = d['menus_appeared']
                times_appeared = d['times_appeared']
                first_appeared = d['first_appeared']
                last_appeared = d['last_appeared']
                lowest_price = d['lowest_price']
                highest_price = d['highest_price']
                cur.execute("INSERT OR IGNORE INTO Dishes (key, name, menus_appeared, times_appeared, first_appeared, last_appeared, lowest_price, highest_price) VALUES (?,?,?,?,?,?,?,?)", (last_key+key, name, menus_appeared, times_appeared, first_appeared, last_appeared, lowest_price, highest_price))
                row_count = cur.rowcount
                if row_count > 0:
                    key += 1
                    conn.commit()
            else:
                break
        continue
    conn.commit()


def calculate_avg_price(cur, conn):
    """
    This function selects the dish name and the highest and lowest prices it has been listed for from the database.
    With this data, the average price is calculated by adding the two prices together and dividing it by two, then creating a tuple with the name and the average price.
    This function returns a sorted list of the tuples in descending order.
    """
    data = cur.execute("SELECT name, highest_price, lowest_price FROM Dishes").fetchall()
    conn.commit()
    
    dish_prices = []
    for tup in data:
        if tup[1] != None:
            high_price = float(tup[1].strip('$'))
            low_price = float(tup[2].strip('$'))
            dish_prices.append((tup[0], high_price, low_price))
        else:
            continue
    sorted_dish_prices = sorted(dish_prices)
    lst_avg_prices = []
    for dish in sorted_dish_prices:
        avg_price = (dish[1] + dish[2]) / 2
        lst_avg_prices.append((dish[0], avg_price))
    sorted_lst_avg_prices = sorted(lst_avg_prices, key = lambda x: x[1], reverse = True)
    return sorted_lst_avg_prices


def write_calculation(cur, conn):
    """
    This function writes the dish names and average prices to a csv file.
    This function does not return anything.
    """
    dish_prices = calculate_avg_price(cur, conn)
    with open('dishprices.txt', 'w') as f:
        f.write('The Average Prices of Dishes Featured in the NYPL Menus API:')
        f.write('\n')
        for dish in dish_prices:
            f.writelines('The average price of ' + str(dish[0]) + ' is ' + str(dish[1]) + '.')
            f.write('\n')
    f.close()


def plot_avg_prices(cur, conn):
    """
    This function plots the top 10 highest average prices from what the list returned by the calculate_avg_price function.
    The graph is a bar graph with the dish names on the x-axis and the average prices on the y-axis. Each value has a color in rainbow order.
    As 25 additional items are added to the database when the function is run repeatedly (for four times), the bar graph updates to display the top 10 highest prices.
    When run, this function displays the bar graph.
    """
    data = calculate_avg_price(cur, conn)[:10]
    items = []        
    prices = []
    for i in range(len(data)):
        items.append(data[i][0])
        prices.append(data[i][1])
    fig = go.Figure(data = go.Bar(name = "Dishes", x=items, y=prices, marker_color = ['red','orange','yellow','green','aqua','blue','mediumorchid','pink','grey','black']))
    title_str = "The top 10 highest average prices (in dollars) of menu items featured in the historic NYPL database"
    x_str = "Dish"
    y_str = "Average Price (dollars)"
    fig.update_layout(title = title_str, xaxis_tickangle=-45, barmode='group',
                xaxis = {'tickmode':'linear', 'title': x_str}, yaxis = {'title': y_str})
    fig.show()

def main():
    cur, conn = setUpDatabase('college_cooks.db')
    web=get_data_from_website('https://www.opentable.com/lists/top-100-2021')
    try:
        cur.execute("SELECT count(*) FROM restaurants_table")
        counts=cur.fetchall()
        counts[0]
    except:
        create_table(cur,conn)
    setup_restaurantstable(web, cur, conn)
    calculate_average(cur,conn)
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
    plt.axis('equal')
    plt.title("Top 10 Main Ingredients For Meals", loc="right")
    plt.tight_layout()
    plt.show()
    create_dish_table(cur, conn)
    calculate_avg_price(cur, conn)
    write_calculation(cur, conn)
    plot_avg_prices(cur, conn)

if __name__ == "__main__":
    main()

