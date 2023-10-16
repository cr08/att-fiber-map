import sqlite3
import requests
import json
import sys
import time

try:
    input = open("addresses.db")
except OSError as error:
    print("SQLite database addresses.db not found. Please run the import.py script to generate an address database. Review the README.md for more information.")
    sys.exit(1)

connection = sqlite3.connect('addresses.db')
cursor = connection.cursor()

cursor.execute("SELECT * FROM addresses WHERE lightGig = 0 ORDER BY updated ASC")

rows = cursor.fetchall()
totalcount = len(rows)

count = 0

for row in rows:
    try:

        row_id = str(row[0])
        row_lon = str(row[1])
        row_lat = str(row[2])
        row_streetnum = str(row[3])
        row_street = str(row[4])
        row_zip = str(row[9])
        row_fiberavail = str(row[12])
        row_availtime = str(row[13])
        row_updated = str(row[14])

        availability_url = 'https://www.att.com/services/shop/model/ecom/shop/view/unified/qualification/service' \
                    '/CheckAvailabilityRESTService/invokeCheckAvailability'

        json_data = {
            'userInputZip': row_zip,
            'userInputAddressLine1': row_streetnum + " " + row_street,
            'mode': 'fullAddress',
            'customer_type': 'Consumer',
            'dtvMigrationFlag': False
        }
        headers = {'content-type': 'application/json'}
        fiber_avail = False

        print("Checking \033[1;33m" + row_streetnum + " " + row_street + ", " + row_zip + "\033[1;0m...  ", end="", flush=True)

        try:
            resp = requests.post(availability_url, data = json.dumps(json_data), headers = headers)
            resp_json = json.loads(resp.text)
            fiber_avail = resp_json['profile']['isGIGAFiberAvailable']
        except:
            print("Unexpected error:", sys.exc_info()[0])

        count = count + 1

        if fiber_avail:
            print("\033[1;32mFiber IS available!\033[1;0m " + count + "/" + totalcount)
            if row_fiberavail is False:
                curtime = str(time.time())
                cursor.execute("""UPDATE addresses SET lightgig = 1, time = ?, updated = ? WHERE id = ?;""", (curtime, curtime, row_id))
                # sql_update_query = "UPDATE addresses SET lightGig = 1, time = " + curtime + ", updated = " + curtime + "WHERE id = " + row_id
                # cursor.execute(sql_update_query)
            else:
                curtime = str(time.time())
                cursor.execute("""UPDATE addresses SET lightgig = 1, updated = ? WHERE id = ?;""", (curtime, row_id))
                # sql_update_query = "UPDATE addresses SET lightGig = 1, updated = " + curtime + "WHERE id = " + row_id
                # cursor.execute(sql_update_query)
        else:
            print("\033[1;31mFiber is NOT available.\033[1;0m " + count + "/" + totalcount)
            curtime = str(time.time())
            cursor.execute("""UPDATE addresses SET lightgig = 0, updated = ? WHERE id = ?;""", (curtime, row_id))
            # sql_update_query = "UPDATE addresses SET lightGig = 0, updated = " + curtime + "WHERE id = " + row_id
            # cursor.execute(sql_update_query)

    except KeyboardInterrupt:
        print("Script cancelled. Writing and closing DB.")
        break

connection.commit()
connection.close()