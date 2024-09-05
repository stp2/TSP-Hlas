#!/usr/bin/python3
# find all routes between all pointes in positions.csv
# max 100 points
# uses time as metrice

import json
import requests
import pickle
from os.path import isfile
import fast_tsp
import gpxpy
import gpxpy.gpx

class Person:
    name: str
    position: str
    index: int
    def __init__(self, index: int, line: str):
        line.strip()
        line = line[:-1]
        data = line.rsplit(",")
        self.name = data[0]
        self.position = ",".join(data[1:])
        self.index = index

index: int = 0
persons: list[Person] = []
key: str
matrix: list[list[int]] = []

with open("key.api", "r") as f:
    key = f.readline()
    key = key[:-1]


with open("positions.csv", "r") as pos:
    for l in pos:
        persons.append(Person(index, l))
        index += 1
    p = [o.__dict__ for o in persons]

if not isfile('data.pkl'):
    url = 'https://api.mapy.cz/v1/routing/matrix-m'
    headers = {'accept': 'application/json'}
    for p in persons:
        payload = {}
        payload['starts'] = p.position
        payload['ends'] = []
        for e in persons:
            payload['ends'].append(e.position)
        payload['routeType'] = 'bike_road'
        payload['apikey'] = key
        r = requests.get(url=url, headers=headers, params=payload)
        mat = r.json()
        matrix.append([])
        for res in mat['matrix'][0]:
            matrix[p.index].append(res['duration'])
# Serialize the object to a binary format
    with open('data.pkl', 'wb') as file:
        pickle.dump(matrix, file)
else:
# Deserialize the object from the binary file
    with open('data.pkl', 'rb') as file:
        matrix = pickle.load(file)

tour = fast_tsp.find_tour(matrix)

# compute path
gpx = gpxpy.gpx.GPX()
points: list[gpxpy.gpx.GPXTrackPoint] = []
for i in range(0, len(tour)):
    s = tour[i]
    e = tour[(i+1)%len(tour)]
    url = 'https://api.mapy.cz/v1/routing/route'
    headers = {'accept': 'application/json'}
    payload = {}
    payload['start'] = persons[s].position
    payload['end'] = persons[e].position
    payload['routeType'] = 'bike_road'
    payload['apikey'] = key
    payload['format'] = 'geojson'
    r = requests.get(url=url, headers=headers, params=payload)
    route = r.json()
    Jpoints = route['geometry']['geometry']['coordinates']
    gpx.waypoints.append(gpxpy.gpx.GPXWaypoint(Jpoints[0][1], Jpoints[0][0], name=persons[s].name))
    for p in Jpoints:
        points.append(gpxpy.gpx.GPXTrackPoint(p[1], p[0]))

track = gpxpy.gpx.GPXTrack("Hlas")
gpx.tracks.append(track)
segment = gpxpy.gpx.GPXTrackSegment(points)
track.segments.append(segment)
with open("route.gpx", "w") as r:
    r.write(gpx.to_xml())
