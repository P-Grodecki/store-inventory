from collections import OrderedDict
import csv
from datetime import datetime
import os

from peewee import *

db = SqliteDatabase('inventory.db')

class Product(Model):
    product_id = PrimaryKeyField()    #primary key
    product_name = CharField(max_length=255,unique=True)
    product_quantity = IntegerField(default=0)
    product_price = IntegerField(default=0)
    date_updated = DateTimeField(default=datetime.now)

    class Meta:
        database = db

def initialize():
    """Initialize the database and the tables if they do not exist."""
    db.connect()
    db.create_tables([Product], safe=True)

def import_from_csv():
    """Import the data from the inventory.csv file as a dictionary"""
    with open('inventory.csv', newline='') as csvfile:
        inventory_reader = csv.DictReader(csvfile)
        inventory_list = list(inventory_reader)
    for row in inventory_list:
        # ReAssign data from string to appropriate data types
        row['product_price'] = round(float(row['product_price'].replace('$',''))*100,0)
        row['product_quantity'] = int(row['product_quantity'])
        row['date_updated'] = datetime.strptime(row['date_updated'], '%m/%d/%Y')
        write_to_db(row)
        # try:
        #     #Create new record in database
        #     Product.create(**row)
        # except IntegrityError:
        #     # Find the other record with a matching name
        #     matching_record = Product.get(product_name=row['product_name'])
        #     # If the current row is more recent than existing record, then update record
        #     if row['date_updated'] > matching_record.date_updated:
        #         #print(matching_record.product_name)
        #         #print(row['date_updated'].strftime('%m/%d/%Y') + " > " + matching_record.date_updated.strftime('%m/%d/%Y'))
        #         matching_record.product_price = row['product_price']
        #         matching_record.product_quantity = row['product_quantity']
        #         matching_record.date_updated = row['date_updated']
        #         matching_record.save()

"""         # product_name,product_price,product_quantity,date_updated
        print(row['product_name'] + " " + str(type(row['product_name'])) +
            str(row['product_price']) + " " + str(type(row['product_price'])) +
            str(row['product_quantity']) + " " + str(type(row['product_quantity'])) +
            row['date_updated'].strftime('%m/%d/%Y') + " " + str(type(row['date_updated']))
            ) """

def write_to_db(row):
    """Given a dictionary of a row instance, write the row to the database.
    If a duplicate row is identified, then only update the record if new row was more recently updated."""
    
    try:
        #Create new record in database
        Product.create(**row)
    except IntegrityError:
        # Find the other record with a matching name
        matching_record = Product.get(product_name=row['product_name'])
        # If the current row is more recent than existing record, then update record
        if row['date_updated'] > matching_record.date_updated:
            #print(matching_record.product_name)
            #print(row['date_updated'].strftime('%m/%d/%Y') + " > " + matching_record.date_updated.strftime('%m/%d/%Y'))
            matching_record.product_price = row['product_price']
            matching_record.product_quantity = row['product_quantity']
            matching_record.date_updated = row['date_updated']
            matching_record.save()


def display_welcome_message(welcome_message):
    print("="*len(welcome_message))
    print(welcome_message)
    print("="*len(welcome_message))

def display_menu():
    #Display Title
    clear()
    display_welcome_message("---- Welcome to th Product List Management Tool ---")
    #Display Main Menu
    while True:
        print('------- MAIN MENU -------')
        print("(Enter 'q' to quit at any time.)")
        print()
        for key, value in menu.items():
            print('{}) {}'.format(key, value.__doc__))
        choice = input("Select an option >>  ").lower().strip()
        if choice in menu:
            clear()
            menu[choice]() 
        elif choice == 'q':
            break
        else:
            clear()
            print('Entry not an option. Try again.')

def existing_product():
    """View product details for a specified product ID#."""
    while True:
        display_welcome_message("View product details for a specified product ID#."+
                                "\n(Enter [b] to return to main menu.)")
        user_id_choice = input('Enter a Product ID:').strip()
        if user_id_choice.lower() == 'b':
            #Exit this loop
            clear()
            break
        try:
            # Find the matching record and print the formatted details for each field.
            matching_record = Product.get(product_id=user_id_choice)
            print()
            print(f'Product ID: {matching_record.product_id}')
            print(f'Product Name: {matching_record.product_name}')
            print('Product Price: ${:.2f}'.format(matching_record.product_price/100))
            print(f'Quantity in Stock: {matching_record.product_quantity}')
            print(f"Last Updated: {matching_record.date_updated.strftime('%m/%d/%Y')}")
            print()
            if input('Press any key to continue.').lower().strip() == 'b':
                clear()
                break
            clear()
        except:
            
            clear()
            print('Product with Entered ID does not exist. Try again.')


def new_product():
    """Add a new product to the database."""
    display_welcome_message("Add a new product to the database.")
    input('Press any key to continue.')
    clear()

def backup_db():
    """Save a backup of the current product database."""
    display_welcome_message("Save a backup of the current product database.")
    input('Press any key to continue.')
    clear()

def clear():
    os.system('cls' if os.name == 'nt' else clear)


menu = OrderedDict([
        ('v', existing_product),
        ('a', new_product),
        ('b', backup_db)
])


if __name__ == '__main__':
    initialize()
    import_from_csv()
    display_menu()

    db.close()
    clear()
    print("Thank you for using the product management tool.\nGoodbye.")
