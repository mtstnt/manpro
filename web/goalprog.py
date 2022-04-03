import pandas as pd
import pyomo.environ as pyo
import openrouteservice as ors
import os

def get_distance_and_duration(client: ors.Client, lat1, lon1, lat2, lon2): 
    routes = client.directions(((lon1, lat1), (lon2, lat2)), profile='driving-car')
    return {
            "distance": routes.get('routes')[0]['summary']['distance'], 
            "duration": routes.get('routes')[0]['summary']['duration']
        }

def match(customers: pd.DataFrame, drivers: pd.DataFrame) -> list[tuple[int, int]]:
    customers = customers.to_dict('records')
    drivers = drivers.to_dict('records')

    weights = {
        'distance': { 'target': 10000, 'positive': 1, 'negative': -1 },
        'duration': { 'target': 5, 'positive': 1, 'negative': -1 },
        'order_count': { 'target': 20, 'positive': 1, 'negative': -1 },
        'rating': { 'target': 3, 'positive': -1, 'negative': 1 },
    }

    # Simpan key dari ORS
    key = os.getenv('OPENROUTESERVICE_KEY')
    client = ors.Client(key=key, base_url='https://api.openrouteservice.org/')
    memo = {}

    data = {}
    for d in drivers:
        d_id = d['id']
        data[d_id] = {}
        for c in customers:
            c_id = c['id']
            result = memo.get((d['latitude'], d['longitude'], c['latitude'], c['longitude']))
            if result is None:
                result = get_distance_and_duration(client, d['latitude'], d['longitude'], c['latitude'], c['longitude'])
                memo[(d['latitude'], d['longitude'], c['latitude'], c['longitude'])] = result

            data[d_id][c_id] = {
                "distance": result['distance'],
                "duration": result['duration'],
                "order_count": d['order_count'],
                "rating": d['rating'],
            }

    result, model = construct_model(weights, data)

    result = []
    ind = 0
    for d in drivers:
        for c in customers:
            if model.x[d, c]() == 1:
               result.append((d, c)) 

    return result


# Define Objective
def get_penalty(target, val, positive):
    if positive:
        if val > target: return val - target
        else: return 0
    else:
        if val < target: return target - val
        else: return 0

# Penalty = (weight positive * X * deviasi dgn target / 1% dari target)
def penalty(model: pyo.Model, weights: dict, data: list[list[dict]], c: int, d: int, param: str):
    m = weights[param]
    return (
        (m['positive'] * model.x[d, c] * get_penalty(m['target'], data[d][c][param], True) / m['target'] / 100)+ 
        (m['negative'] * model.x[d, c] * get_penalty(m['target'], data[d][c][param], False) / m['target'] / 100)
    )

def construct_model(weights: dict, data: list[list[dict]]) -> pyo.ConcreteModel:
    # Model pyomo utk solve GP
    model = pyo.ConcreteModel()
    model.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)

    # Define Variables
    drivers = [d['id'] for d in drivers]
    customers = [c['id'] for c in customers]

    model.x = pyo.Var(drivers, customers, domain=pyo.NonNegativeIntegers)

    # Objective fn = Sum of penalty semua bidang.
    model.Cost = pyo.Objective(
        expr = sum([
            penalty(model, weights, data, c, d, 'distance') + 
            penalty(model, weights, data, c, d, 'duration') + 
            penalty(model, weights, data, c, d, 'order_count') + 
            penalty(model, weights, data, c, d, 'rating') 
            for c in customers for d in drivers
        ]),
        sense = pyo.minimize)

    # Define Constraint
    # Constraint = jumlah dari setiap Driver dengan semua pasangan Clientnya adalah 1
    model.driver = pyo.ConstraintList()
    for d in drivers:
        model.driver.add(sum(model.x[d, c] for c in customers) == 1)

    model.customer = pyo.ConstraintList()
    for c in customers:
        model.customer.add(sum(model.x[d, c] for d in drivers) == 1)

    result = pyo.SolverFactory('cbc').solve(model)
    return [result, model]