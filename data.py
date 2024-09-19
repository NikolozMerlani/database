import sqlite3

class Database:
    def __init__(self, db_file):
        self.db_file = db_file
        self.create_tables()

    def create_tables(self):
        
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS cars (
                car_id INTEGER PRIMARY KEY AUTOINCREMENT,
                manufacturer TEXT NOT NULL,
                model TEXT NOT NULL
            )
            ''')
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cid INTEGER NOT NULL,
                color TEXT,
                date TEXT,
                price REAL,
                FOREIGN KEY (cid) REFERENCES cars (car_id)
            )
            ''')
            connection.commit()

    def add_car(self, manufacturer, model, color, date, price):
        
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            try:
                cursor.execute('''
                INSERT INTO cars (manufacturer, model)
                VALUES (?, ?)
                ''', (manufacturer, model))
                
                car_id = cursor.lastrowid  

                cursor.execute('''
                INSERT INTO info (cid, color, date, price)
                VALUES (?, ?, ?, ?)
                ''', (car_id, color, date, price))

                connection.commit()
                print("Car and info added successfully!")
            except Exception as e:
                print(f"An error occurred: {e}")

    def update_car_and_info(self, car_id, update_car=False, update_info=False, new_manufacturer=None, new_model=None, new_color=None, new_date=None, new_price=None):
        
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            try:
                
                if update_car:
                    cursor.execute('''
                    UPDATE cars
                    SET manufacturer = COALESCE(?, manufacturer), model = COALESCE(?, model)
                    WHERE car_id = ?
                    ''', (new_manufacturer, new_model, car_id))

                
                if update_info:
                    cursor.execute('''
                    UPDATE info
                    SET color = COALESCE(?, color), date = COALESCE(?, date), price = COALESCE(?, price)
                    WHERE cid = ?
                    ''', (new_color, new_date, new_price, car_id))

                connection.commit()
                print("Car and/or info updated!")
            except Exception as e:
                print(f"An error occurred: {e}")

    def delete_car_and_info(self, car_number):
        
        car_id = self._get_car_id_by_number(car_number)
        if not car_id:
            print("Invalid car number.")
            return

        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            try:
                
                cursor.execute('DELETE FROM info WHERE cid = ?', (car_id,))

                
                cursor.execute('DELETE FROM cars WHERE car_id = ?', (car_id,))

                connection.commit()
                print("Car and info deleted!")
            except Exception as e:
                print(f"An error occurred: {e}")

    def _get_car_id_by_number(self, number):
        
        cars = self.get_all_cars()
        if 1 <= number <= len(cars):
            return cars[number - 1][0]  
        print("Invalid car number.")
        return None

    def get_all_cars(self):
        
        query = '''
        SELECT c.car_id, c.manufacturer, c.model, i.color, i.date, i.price
        FROM cars c
        JOIN info i ON c.car_id = i.cid
        '''

        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            cursor.execute(query)
            return cursor.fetchall()

    def show_cars(self, filter_type=None, filter_value=None):
        
        if filter_type == "year":
            query = '''
            SELECT c.car_id, c.manufacturer, c.model, i.color, i.date, i.price
            FROM cars c
            JOIN info i ON c.car_id = i.cid
            WHERE i.date LIKE ?
            '''
            params = (f'{filter_value}%',)
        elif filter_type == "color":
            query = '''
            SELECT c.car_id, c.manufacturer, c.model, i.color, i.date, i.price
            FROM cars c
            JOIN info i ON c.car_id = i.cid
            WHERE i.color = ?
            '''
            params = (filter_value,)
        elif filter_type == "price":
            query = '''
            SELECT c.car_id, c.manufacturer, c.model, i.color, i.date, i.price
            FROM cars c
            JOIN info i ON c.car_id = i.cid
            WHERE i.price = ?
            '''
            params = (filter_value,)
        else:
            query = '''
            SELECT c.car_id, c.manufacturer, c.model, i.color, i.date, i.price
            FROM cars c
            JOIN info i ON c.car_id = i.cid
            '''
            params = ()

        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            cursor.execute(query, params)
            entries = cursor.fetchall()
            if entries:
                for index, entry in enumerate(entries, start=1):
                    print("-" * 25 + str(index) + "-" * 25)
                    print(f"ID: {entry[0]}")
                    print(f"Manufacturer: {entry[1]}")
                    print(f"Model: {entry[2]}")
                    print(f"Color: {entry[3]}")
                    print(f"Date: {entry[4]}")
                    print(f"Price: {entry[5]}")
                    print("-" * 51)
            else:
                print("No cars found.")

class Manager:
    def __init__(self, database):
        self.database = database

    def add_car(self, manufacturer, model, color, date, price):
        self.database.add_car(manufacturer, model, color, date, price)

    def update_car_and_info(self, car_number, update_car=False, update_info=False, new_manufacturer=None, new_model=None, new_color=None, new_date=None, new_price=None):
        car_id = self.database._get_car_id_by_number(car_number)
        if car_id:
            self.database.update_car_and_info(car_id, update_car, update_info, new_manufacturer, new_model, new_color, new_date, new_price)

    def delete_car_and_info(self, car_number):
        self.database.delete_car_and_info(car_number)

    def show_cars(self, filter_type=None, filter_value=None):
        self.database.show_cars(filter_type, filter_value)

def menu():
    database = Database('cars.db')
    manager = Manager(database)

    while True:
        print("\nCar Management Menu:")
        print("1) Add Car")
        print("2) Update Car and Info")
        print("3) Delete Car and Info")
        print("4) Show Cars")
        print("5) Quit\n")

        choice = input("Choose an action: ").strip()

        if choice == "5":
            print("Exiting...")
            break

        elif choice == "1":
            manufacturer = input("Enter car manufacturer: ")
            model = input("Enter car model: ")
            color = input("Enter car color: ")
            date = input("Enter production date (YYYY-MM-DD): ")
            price_input = input("Enter price: ")
            try:
                price = float(price_input)
            except ValueError:
                print("Invalid price entered. Please enter a numeric value.")
                continue
            manager.add_car(manufacturer, model, color, date, price)

        elif choice == "2":
            manager.show_cars()  
            car_number = int(input("Enter car number to update: "))
            print("\nUpdate Options:")
            print("1) Update Car Details")
            print("2) Update Info Details")
            print("3) Update Both Car and Info")
            update_choice = input("Choose update option: ").strip()

            if update_choice == "1":
                new_manufacturer = input("Enter new manufacturer (leave blank to keep current): ")
                new_model = input("Enter new model (leave blank to keep current): ")
                manager.update_car_and_info(car_number, update_car=True, update_info=False, new_manufacturer=new_manufacturer if new_manufacturer else None, new_model=new_model if new_model else None)
            elif update_choice == "2":
                new_color = input("Enter new color (leave blank to keep current): ")
                new_date = input("Enter new production date (YYYY-MM-DD) (leave blank to keep current): ")
                new_price_input = input("Enter new price (leave blank to keep current): ")
                try:
                    new_price = float(new_price_input) if new_price_input else None
                except ValueError:
                    print("Invalid price entered. Please enter a numeric value.")
                    continue
                manager.update_car_and_info(car_number, update_car=False, update_info=True, new_color=new_color if new_color else None, new_date=new_date if new_date else None, new_price=new_price)
            elif update_choice == "3":
                new_manufacturer = input("Enter new manufacturer (leave blank to keep current): ")
                new_model = input("Enter new model (leave blank to keep current): ")
                new_color = input("Enter new color (leave blank to keep current): ")
                new_date = input("Enter new production date (YYYY-MM-DD) (leave blank to keep current): ")
                new_price_input = input("Enter new price (leave blank to keep current): ")
                try:
                    new_price = float(new_price_input) if new_price_input else None
                except ValueError:
                    print("Invalid price entered. Please enter a numeric value.")
                    continue
                manager.update_car_and_info(car_number, update_car=True, update_info=True, new_manufacturer=new_manufacturer if new_manufacturer else None, new_model=new_model if new_model else None, new_color=new_color if new_color else None, new_date=new_date if new_date else None, new_price=new_price)
            else:
                print("Invalid option.")

        elif choice == "3":
            manager.show_cars()  
            car_number = int(input("Enter car number to delete: "))
            manager.delete_car_and_info(car_number)

        elif choice == "4":
            print("\nShow Cars Options:")
            print("1) Show All Cars")
            print("2) Filter by Year")
            print("3) Filter by Color")
            print("4) Filter by Price")
            filter_choice = input("Choose filter option: ").strip()

            if filter_choice == "1":
                manager.show_cars()
            elif filter_choice == "2":
                year = input("Enter year (YYYY): ")
                manager.show_cars(filter_type="year", filter_value=year)
            elif filter_choice == "3":
                color = input("Enter color: ")
                manager.show_cars(filter_type="color", filter_value=color)
            elif filter_choice == "4":
                price_input = input("Enter price: ")
                try:
                    price = float(price_input)
                except ValueError:
                    print("Invalid price entered. Please enter a numeric value.")
                    continue
                manager.show_cars(filter_type="price", filter_value=price)
            else:
                print("Invalid option.")

        else:
            print("Invalid action! Please choose a valid option.")

menu()
