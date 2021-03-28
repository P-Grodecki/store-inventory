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

def import_from_csv(backup_file):
    """Import the data from the inventory.csv file as a dictionary"""
    with open(backup_file, newline='') as csvfile:
        inventory_reader = csv.DictReader(csvfile)
        inventory_list = list(inventory_reader)
    for row in inventory_list:
        # ReAssign data from string to appropriate data types
        row = format_product_data_to_db(row['product_name'], row['product_price'], row['product_quantity'], row['date_updated'])
        write_to_db(row)

def format_product_data_to_db(arg_name, arg_price, arg_quantity, arg_date):
    """Given the string name, decimal price, integer quantity, and '%m/%d/%Y' date, create formatted row dictionary."""
    try:
        data = {}
        data['product_name'] = arg_name
        data['product_price'] = int(round(float(arg_price.replace('$',''))*100,0))
        data['product_quantity'] = int(arg_quantity)
        data['date_updated'] = datetime.strptime(arg_date, '%m/%d/%Y')
    except ValueError:
        print('Oops! One of the entered values was not the correct data type.')
        data = False
    return data

def write_to_db(row):
    """Given a dictionary of a row instance, write the row to the database.
    If a duplicate row is identified, then only update the record if new row was more recently updated."""
    try:
        # Create new record in database
        Product.create(**row)
        # Return True to denote successful addition to DB
        return True
    except IntegrityError:
        # Find the other record with a matching name
        matching_record = Product.get(product_name=row['product_name'])
        # If the current row is more recent than existing record, then update record
        if row['date_updated'] >= matching_record.date_updated:
            matching_record.product_price = row['product_price']
            matching_record.product_quantity = row['product_quantity']
            matching_record.date_updated = row['date_updated']
            matching_record.save()
            # Return string denoting that a row was updated.
            return False

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
    """View a single product's inventory."""
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
            format_product_data_from_db(matching_record, True, True)
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
    print()
    new_name = input('Product Name:     ')
    new_quantity = input('Product Quantity: ')
    new_price = input('Product Price:    $')
    new_date = datetime.now().strftime('%m/%d/%Y')
    the_formatted_data = format_product_data_to_db(new_name, new_price, new_quantity, new_date)
    if the_formatted_data == False:
        input('Product not added to inventory.\n' +
                'Returning to Main Menu. Press any key to continue...')
    else:
        write_results = write_to_db(the_formatted_data)
        if write_results == True:
            input(f"Successfully added '{new_name}' to product inventory.\n" +
                    'Returning to Main Menu. Press any key to continue')
        else:
            input(f"Product already exists, successfully updated '{new_name}' in product inventory.\n" +
                    'Returning to Main Menu. Press any key to continue')
    clear()

def backup_db():
    """Make a backup of the entire inventory."""
    display_welcome_message("Save a backup of the current product database.")
    
    with open('backup.csv', 'w') as csv_backup_file:
        field_names = ['product_name',
                        'product_quantity',
                        'product_price',
                        'date_updated',
        ]
        write_backup = csv.DictWriter(csv_backup_file, field_names)
        write_backup.writeheader()

        all_records = Product.select()
        for record in all_records:
            record_dict = format_product_data_from_db(record, False, False)            
            write_backup.writerow(record_dict)

    input('File sucessfully backed up. Press any key to continue.')
    clear()

def format_product_data_from_db(the_record, to_print, include_id):
    """Given A single record from teh inventory database,
    format the various fields into strings stored in a dictionary.
    Print the formatted fields in user-friendly format.
    Return dictionary of formatted string values."""

    formatted_record = {
        'product_name' : the_record.product_name,
        'product_price' : '${:.2f}'.format(the_record.product_price/100), 
        'product_quantity' : the_record.product_quantity,
        'date_updated' : the_record.date_updated.strftime('%m/%d/%Y'),
    }
    if include_id == True:
        formatted_record['product_id'] = the_record.product_id

    if to_print:
        if include_id == True:
            print('Product ID: {}'.format(formatted_record['product_id']))
        print('Product Name: {}'.format(formatted_record['product_name']))
        print('Product Price: {}'.format(formatted_record['product_price']))
        print('Quantity in Stock: {}'.format(formatted_record['product_quantity']))
        print('Last Updated: {}'.format(formatted_record['date_updated']))
    return formatted_record

def clear():
    os.system('cls' if os.name == 'nt' else clear)


menu = OrderedDict([
        ('v', existing_product),
        ('a', new_product),
        ('b', backup_db)
])

if __name__ == '__main__':
    initialize()
    import_from_csv('inventory.csv')
    #import_from_csv('backup.csv')
    display_menu()
    db.close()
    clear()
    print("Thank you for using the product inventory management tool.\nGoodbye.\n")
