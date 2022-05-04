import csv
import random
import numpy as np

DRIVER_DATA_FILENAME = "./datasets/data_driver_2.csv"
CLIENT_DATA_FILENAME = "./datasets/data_client_2.csv"
BANNED_DATA_FILENAME = "./datasets/banned_data.csv"

n = 1500
r_lat = np.arange(-7.365671, -7.226902, 0.000001)
r_long = np.arange(112.652278, 112.790673, 0.000001)
r_rating = 5
r_order_count = 200
r_total_trip = np.arange(2.0, 10.0, 0.001)
r_time_idle = 7200

header = ["id", "latitude", "longitude", "rating_driver", "order_count", "total_trip", "time_idle"]
with open(DRIVER_DATA_FILENAME, "w", newline="") as f:
    print("Opening CSV")
    writer = csv.writer(f)
    writer.writerow(header)

    print("Creating driver data")
    for i in range(n):
        row = []
        row.append(i)  # id
        row.append(r_lat[random.randint(0, len(r_lat))])  # lat
        row.append(r_long[random.randint(0, len(r_long))])  # long
        row.append(random.randint(1, r_rating))  # rating
        order_count = random.randint(0, r_order_count)
        row.append(order_count)  # order count
        row.append(
            order_count * r_total_trip[random.randint(0, len(r_total_trip))]
        )  # total trip (km)
        row.append(random.randint(0, r_time_idle))  # time idle
        writer.writerow(row)
    print("Driver data created")
print("Closing CSV")


header = ["id", "latitude", "longitude", "rating_client"]
with open(CLIENT_DATA_FILENAME, "w", newline="") as f:
    print("Opening CSV")
    writer = csv.writer(f)
    writer.writerow(header)
    print("Creating driver data")
    for i in range(n):
        row = []
        row.append(i)  # id
        row.append(r_lat[random.randint(0, len(r_lat))])  # lat
        row.append(r_long[random.randint(0, len(r_long))])  # long
        row.append(random.randint(1, r_rating))  # rating
        writer.writerow(row)
    print("Client data created")
print("Closing CSV")

header = ["client_id", "driver_id"]
with open(BANNED_DATA_FILENAME, "w", newline="") as f:
    print("Opening CSV")
    writer = csv.writer(f)
    writer.writerow(header)
    print("Creating banned data")
    for i in range(n):
        row = []
        row.append(r_lat[random.randint(0, n)])  # id client
        row.append(r_long[random.randint(0, n)])  # id driver
        writer.writerow(row)
    print("Banned data created")
print("Closing CSV")