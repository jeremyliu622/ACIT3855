import mysql.connector

db_conn = mysql.connector.connect(host="acit3855jeremy.eastus2.cloudapp.azure.com", user="user",
                                  password="password", database="events")

db_cursor = db_conn.cursor()


db_cursor.execute('''
          CREATE TABLE book_inventory
          (id INT NOT NULL AUTO_INCREMENT, 
           book_id VARCHAR(100) NOT NULL,
           name VARCHAR(100) NOT NULL,
           author VARCHAR(100) NOT NULL,
           category VARCHAR(100) NOT NULL,
           price NUMERIC NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           quantity INTEGER NOT NULL,
           CONSTRAINT book_inventory_pk PRIMARY KEY (id))
          ''')

db_cursor.execute('''
          CREATE TABLE purchase_history
          (id INT NOT NULL AUTO_INCREMENT, 
           book_id VARCHAR(100) NOT NULL,
           purchase_id VARCHAR(100) NOT NULL,
           username VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           quantity INTEGER NOT NULL,
           CONSTRAINT purchase_history_pk PRIMARY KEY (id))
          ''')

db_cursor.close()
