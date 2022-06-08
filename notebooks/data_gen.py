import csv
import random
import numpy as np

DRIVER_DATA_FILENAME = "./datasets/data_driver_fix.csv"
CLIENT_DATA_FILENAME = "./datasets/data_client_fix.csv"
BANNED_DATA_FILENAME = "./datasets/banned_data.csv"

n = 20
r_lat = np.arange(-7.365671, -7.226902, 0.000001)
r_long = np.arange(112.652278, 112.790673, 0.000001)
r_rating = 5

header = ["id", "latitude", "longitude", "rating_driver"]
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
        row.append(random.randint(0, r_rating))  # rating
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
        row.append(random.randint(0, r_rating))  # rating
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
        row.append(random.randint(0, n-1))  # id client
        row.append(random.randint(0, n-1))  # id driver
        writer.writerow(row)
    print("Banned data created")
print("Closing CSV")