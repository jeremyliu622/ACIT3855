import mysql.connector

db_conn = mysql.connector.connect(host="acit3855jeremy.eastus2.cloudapp.azure.com", user="user",
                                  password="password", database="events")
db_cursor = db_conn.cursor()

db_cursor.execute('''
          DROP TABLE book_inventory
          ''')

db_cursor.execute('''
          DROP TABLE purchase_history
          ''')

db_cursor.close()
