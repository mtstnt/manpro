import requests as req
import pandas as pd
import pyomo.environ as pyo
import os
from sklearn.preprocessing import minmax_scale

memo = {}

def match(
    clients: pd.DataFrame, drivers: pd.DataFrame, banned: pd.DataFrame
) -> list[tuple[int, int]]:

    clients = clients[0:20]
    drivers = drivers[0:20]
    # Max latitude, longitude dari dummy harus bisa menggambarkan situasi terburuk (posisi terjauh)
    # Tapi juga menggambarkan posisi driver kurang lebih. Jadi dummy itu merepresentasikan jarak terjauh dari rata-rata driver.
    driver_lat_avg = drivers["latitude"].mean()
    driver_long_avg = drivers["longitude"].mean()

    client_lat_avg = clients["latitude"].mean()
    client_long_avg = clients["longitude"].mean()

    # Cek apakah data balanced/imbalanced
    if len(clients) > len(drivers):
        # Add dummy drivers
        addition = abs(len(clients)) - abs(len(drivers))
        for i in range(addition):
            print(drivers.tail(1).iloc[0]["id"] + 1)
            drivers = drivers.append(
                {
                    "id": drivers.tail(1).iloc[0]["id"] + 1,
                    "latitude": driver_lat_avg,
                    "longitude": driver_long_avg,
                    "rating_driver": 0.0,
                },
                ignore_index=True,
            )

    elif len(clients) < len(drivers):
        # Add dummy clients
        addition = abs(len(clients)) - abs(len(drivers))
        for i in range(addition):
            clients = clients.append(
                {
                    "id": clients.tail(1).iloc[0]["id"] + 1,
                    "latitude": client_lat_avg,
                    "longitude": client_long_avg,
                    "rating_client": 0.0,
                },
                ignore_index=True,
            )

    # Normalisasi
    clients["rating_client_scaled"] = minmax_scale(clients["rating_client"])
    drivers["rating_driver_scaled"] = minmax_scale(drivers["rating_driver"])

    # Ambil data sbg list
    drivers_data = drivers.to_dict("records")
    clients_data = clients.to_dict("records")

    banned_data = None
    if banned != None:
        banned_data = banned.to_dict("records")

    locations = []
    for i in drivers_data:
        locations.append((i["longitude"], i["latitude"]))
    for i in clients_data:
        locations.append((i["longitude"], i["latitude"]))

    distances, durations, distances_ori, durations_ori = get_location_info(locations)

    # Definisikan weight.
    # Weight pada kondisi positif dan negatif, negatif berarti cenderung untuk lebih dipilih karena
    #  menggunakan metode Minimize pada rumus.

    weights = {
        'distance'      : { 'target': 0, 'positive': 1, 'negative': -1 },
        'duration'      : { 'target': 0, 'positive': 1, 'negative': -1 },
        'rating'        : { 'target': 0, 'positive': 1, 'negative': -1 },
    }

    # Karena data yang berpengaruh hanya data yang digabungkan antara keduanya, 
    #   maka kami mengumpulkan data setelah dirumuskan dari masing-masing pasangan penumpang-driver
    data: dict[tuple, dict[str, any]] = {}
    for d in drivers_data:
        d_id = d['id']
        data[d_id] = {}
        for c in clients_data:
            c_id = c['id']

            distance = distances[(d['longitude'], d['latitude'])][(c['longitude'], c['latitude'])]
            duration = durations[(d['longitude'], d['latitude'])][(c['longitude'], c['latitude'])]

            distance_ori = distances_ori[(d['longitude'], d['latitude'])][(c['longitude'], c['latitude'])]
            duration_ori = durations_ori[(d['longitude'], d['latitude'])][(c['longitude'], c['latitude'])]

            rating = abs(d['rating_driver_scaled'] - c['rating_client_scaled'])

            data[d_id][c_id] = {
                "distance": distance,
                "duration": duration,
                
                "rating": rating,

                # For validation
                "rating_client": c['rating_client_scaled'],
                "rating_driver": d['rating_driver_scaled'],

                "distance_ori": distance_ori,
                "duration_ori": duration_ori,

                "rating_client_ori": c['rating_client'],
                "rating_driver_ori": d['rating_driver'],
            }

        # Model pyomo utk solve GP
    model = pyo.ConcreteModel()
    model.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)

    # Variabel yang digunakan untuk mengidentifikasi driver dan customer adalah ID.
    drivers = [d['id'] for d in drivers_data]
    clients = [c['id'] for c in clients_data]

    # Mendaftarkan semua kombinasi antara ID driver dan client.
    model.x = pyo.Var(drivers, clients, domain=pyo.NonNegativeIntegers)

    # Rumus untuk menghitung penalty negatif dan positif
    def get_penalty(target, val, positive=True):
        if positive:
            if val > target: return val - target
            else: return 0
        else:
            if val < target: return target - val
            else: return 0

    # Penalty = (weight positive * X * deviasi dgn target apabila >) + (weight negatif * X * deviasi dgn target apabila <)
    # Salah satu dari deviasi ini akan menjadi 0 (target: 3, val: 5 maka sisi negatif akan 0)
    def penalty(c, d, param):
        m = weights[param]
        return (
            (m['positive'] * model.x[d, c] * get_penalty(m['target'], data[d][c][param], True)) + 
            (m['negative'] * model.x[d, c] * get_penalty(m['target'], data[d][c][param], False))
        )

    # Hitung penalti dari matching yang sesuai (DV jadi 1.0)
    # Ini dipakai di paling terakhir untuk menampilkan perhitungan penalti.
    def v_penalty(c, d, param):
        m = weights[param]
        return (
            (m['positive'] * 1 * get_penalty(m['target'], data[d][c][param], True)) + 
            (m['negative'] * 1 * get_penalty(m['target'], data[d][c][param], False))
        )

    # Objective function: minimalkan jumlah dari semua penalty masing-masing kolom data gabungan.
    model.Cost = pyo.Objective(
        expr = sum([
            penalty(c, d, 'distance') + 
            penalty(c, d, 'duration') +
            penalty(c, d, 'rating')
            for c in clients for d in drivers
        ]),
        sense = pyo.minimize)

    # Constraint yang digunakan yaitu pada jumlah nilai variabel pada setiap driver dengan semua kombinasi pasangan penumpangnya antara 0 atau 1 karena hanya memperbolehkan 1 driver mengambil 1 customer atau tidak mengambil customer sama sekali.

    model.driver = pyo.ConstraintList()
    for d in drivers:
        model.driver.add(sum(model.x[d, c] for c in clients) == 1)

    model.client = pyo.ConstraintList()
    for c in clients:
        model.client.add(sum(model.x[d, c] for d in drivers) == 1)

    # Menambahkan constraint banned untuk pasangan penumpang dan driver yang tidak diperbolehkan ada di hasil matching.
    if banned_data is not None:
        model.banned = pyo.ConstraintList()
        for i in banned_data:
            if i['client_id'] in clients and i['driver_id'] in drivers:
                model.banned.add(model.x[i['driver_id'], i['client_id']] == 0)

    # Gunakan solver utk solve
    pyo.SolverFactory('cbc').solve(model)
    # result.write()

    # Membuat DataFrame hasil
    df = pd.DataFrame([], columns=clients, index=drivers)

    for c in clients:
        mdr = []
        for d in drivers:
            mdr.append(model.x[d, c]())
        df[c] = mdr

    # Hasil akhir ada di variabel ini
    result = df
    raw_calculation_data = data

    # TODO: Ambil hasil data sisanya
    return raw_calculation_data, result

def create_matrix(data, locations):
    durations_matrix, distances_matrix = {}, {}
    durations_matrix_ori, distances_matrix_ori = {}, {}

    # SCALING
    data["durations_original"] = data["durations"]
    data["distances_original"] = data["distances"]

    data["durations_scaled"] = minmax_scale(data["durations"])
    data["distances_scaled"] = minmax_scale(data["distances"])

    for i, src in enumerate(locations):
        distances_matrix[src] = {}
        durations_matrix[src] = {}
        distances_matrix_ori[src] = {}
        durations_matrix_ori[src] = {}

        for j, dest in enumerate(locations):
            durations_matrix[src][dest] = data["durations_scaled"][i][j]
            distances_matrix[src][dest] = data["distances_scaled"][i][j]
            durations_matrix_ori[src][dest] = data["durations_original"][i][j]
            distances_matrix_ori[src][dest] = data["distances_original"][i][j]

    return (
        distances_matrix,
        durations_matrix,
        distances_matrix_ori,
        durations_matrix_ori,
    )


def get_location_info(locations):
    data = memo.get(tuple(locations))

    if data != None:
        print("Cache hit")
        result = create_matrix(data, locations)
        memo[tuple(locations)] = data
        return result

    key = os.getenv("OPENROUTESERVICE_KEY")
    headers = {
        "Authorization": key,
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json, application/geo+json",
    }
    body = {
        "locations": [[i for i in locs] for locs in locations],
        "metrics": ["distance", "duration"],
    }

    res = req.post(
        "https://api.openrouteservice.org/v2/matrix/driving-car",
        json=body,
        headers=headers,
    )

    print(res.status_code)
    if res.status_code == 200:
        data = res.json()
        memo[tuple(locations)] = data
        return create_matrix(data, locations)
    else:
        raise Exception("Error", res.status_code, res.content.decode())


# Define Objective
def get_penalty(target, val, positive):
    if positive:
        if val > target:
            return val - target
        else:
            return 0
    else:
        if val < target:
            return target - val
        else:
            return 0


# Penalty = (weight positive * X * deviasi dgn target / 1% dari target)
def penalty(
    model: pyo.Model, weights: dict, data: list[list[dict]], c: int, d: int, param: str
):
    m = weights[param]
    return (
        m["positive"]
        * model.x[d, c]
        * get_penalty(m["target"], data[d][c][param], True)
        / m["target"]
        / 100
    ) + (
        m["negative"]
        * model.x[d, c]
        * get_penalty(m["target"], data[d][c][param], False)
        / m["target"]
        / 100
    )