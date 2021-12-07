from typing import ItemsView, List, Tuple
from bs4 import BeautifulSoup
import requests
import unittest
import sqlite3
import json
import os
import matplotlib
import matplotlib.pyplot as plt
import random


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


def setUpDatabase(db_name):
    """
    This function creates the database titled "restaurants_database". 
    It returns the connection to the database and the cursor.
    """
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

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

main()






      