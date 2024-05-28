import os
import pymssql
import sys
import subprocess

# MSSQL bağlantı bilgileri
server = 'YourDatabase.net'
database = 'DatBase_Name'
username = 'username'
password = 'password'


# MSSQL bağlantısını oluştur
conn = pymssql.connect(server, username, password, database)
cursor = conn.cursor()

def list_tables():
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE'")
    tables = [table[0] for table in cursor.fetchall()]
    print("The Tables:")
    for idx, table in enumerate(tables, start=1):
        print(f"{idx}. {table}")
    return tables

def add_row(selected_table):
    try:
        # Get column names for the selected table
        cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{selected_table}'")
        columns = [column[0] for column in cursor.fetchall()]
        
        cursor.execute(f"SELECT * FROM {selected_table}")
        all_rows_before = cursor.fetchall()
        for row in all_rows_before:
            print(row)        
    
        # Ask user for values for each column
        new_values = {}
        for column in columns:
            new_values[column] = input(f"Input data here {column}: ")

        # Construct the INSERT query
        insert_query = f"INSERT INTO {selected_table} ({', '.join(columns)}) VALUES ({', '.join(['%s' for _ in columns])})"

        cursor.execute(insert_query, tuple(new_values.values()))
        conn.commit()

        print("New Input added.")
        cursor.execute(f"SELECT * FROM {selected_table}")
        all_rows_after = cursor.fetchall()        
        print("\nThe Updated Table:")
        for row in all_rows_after:
            print(row)

    except pymssql.Error as e:
        print(f"Error adding row: {e}")
        
def edit_table():
    os.system('cls') #cls for windows, remove cmd
    
    try:       
        tables = list_tables()

        # Choose a table to edit
        table_index = int(input("Choose which table will be edit (table number): "))
        selected_table = tables[table_index - 1]

        print(f"Choosed Table: {selected_table}")
        choice = input("400: Edit data\n401: Add Child\n402: Remove Child \nYour Operation: ")
        if choice == "400":

            cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE WHERE TABLE_NAME = '{selected_table}'")
            primary_key_columns = [column[0] for column in cursor.fetchall()]
            # Ask for the primary key value
            primary_key_value = input(f"Input New {primary_key_columns[0]} data: ")
            # Construct the WHERE clause for the primary key
            where_clause = f"{primary_key_columns[0]} = '{primary_key_value}'"
            # Query to find the row based on primary key value
            sql_query = f"SELECT * FROM {selected_table} WHERE {where_clause}"
            cursor.execute(sql_query)
            result = cursor.fetchone()
            if result:
                print("Found number:")
                for col, value in zip(cursor.description, result):
                    print(f"{col[0]}: {value}")
            
            column_to_update = input("Which collumn will be edit -collumn name-: ")
            new_value = input(f"New data for {column_to_update}: ")

            update_query = f"UPDATE {selected_table} SET {column_to_update} = '{new_value}' WHERE {where_clause}"
            cursor.execute(update_query)
            conn.commit()
            # get The Updated line 
            cursor.execute(sql_query)
            updated_result = cursor.fetchone()
            print("The Updated Line:")
            for col, value in zip(cursor.description, updated_result):
                print(f"{col[0]}: {value}")            

        elif choice == "401":
            add_row(selected_table)
            
        elif choice == "402":
            # Display all rows before deletion
            cursor.execute(f"SELECT * FROM {selected_table}")
            all_rows_before = cursor.fetchall()
            print("All lines before update:")
            for row in all_rows_before:
                print(row)

            # Ask for the primary key value
            cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE WHERE TABLE_NAME = '{selected_table}'")
            primary_key_columns = [column[0] for column in cursor.fetchall()]
            primary_key_value = input(f"Input New {primary_key_columns[0]} data: ")

            # Construct the WHERE clause for the primary key
            where_clause = f"{primary_key_columns[0]} = '{primary_key_value}'"
            # Query to find the row based on primary key value
            sql_query = f"SELECT * FROM {selected_table} WHERE {where_clause}"
            cursor.execute(sql_query)
            result = cursor.fetchone()

            if result:
                print("Line will be Remove is: ")
                for col, value in zip(cursor.description, result):
                    print(f"{col[0]}: {value}")

                # Delete the row
                delete_query = f"DELETE FROM {selected_table} WHERE {where_clause}"
                cursor.execute(delete_query)
                conn.commit()
                print("Line Successfully Removed.")

                # Display all rows after deletion
                cursor.execute(f"SELECT * FROM {selected_table}")
                all_rows_after = cursor.fetchall()
                print("\nAll lines at Table (After Delete):")
                for row in all_rows_after:
                    print(row)
            else:
                print("The indexed line is not found -ERROR AT SEARCH LINE [404]-.")

    except (ValueError, IndexError):
        print("Unexpected Login.")
        input("Press any key to continou.")

# Main part of the code
def main_menu():
    os.system('cls')

    # LOGIN HERE
    print("\nChoose your operation.")
    print("0: Exit")        
    print("1: Edit Table")

    choice = input("Operation: ")

    if choice == '1':
        edit_table()

    elif choice == '0':
        sys.exit()
    else:
        print("Unknown Operation.")
            
def azure_login():
    try:
        # Run 'az login' command
        result = subprocess.run(['az', 'login'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Check if the command was successful
        if result.returncode == 0:
            print("Azure login successful")
            main_menu()
        else:
            print("Error during Azure login:")
            print(result.stderr)

    except Exception as e:
        print("An error occurred:", str(e))

azure_login()