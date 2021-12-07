
from logging import fatal
import unittest
import sqlite3
import json
import requests
import os
import csv
import matplotlib
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import urllib3
import pandas as pd

urllib3.disable_warnings()

def setUpDatabase(db_name):
    """
    This function sets up the database 'menus.db' that will be accessed with later functions.
    It returns the connection to the database and the cursor.
    """
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

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
    """
    This function calls all of the above functions.
    It sets up the 'menus.db' database, creates the Dishes table in the database, calculates the average dish prices, writes these calculatinos into a csv file, and plots the data on a bar graph.
    """
    cur, conn = setUpDatabase('college_cooks.db')
    create_dish_table(cur, conn)
    calculate_avg_price(cur, conn)
    write_calculation(cur, conn)
    plot_avg_prices(cur, conn)

if __name__ == "__main__":
    main()