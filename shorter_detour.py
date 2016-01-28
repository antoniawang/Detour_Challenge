import argparse
import json
import os

from urllib2 import urlopen

Google_key = os.environ['GOOGLE_API_KEY'] # sourcing personal Developer API key

def create_dist_dict(A, B, C, D):
	""" Use the Google Directions API to get routing distances
		for all relevant legs between 4 points a driver may take,
		store the distances and coordinates and text of units
		in a dictionary. """

	routes = [(A,B), (C,D), (A,C), (D,B), (C,A), (B,D)]
	
	# for each relevant leg, map the coordinate pair, resulting distance and text for units
	routes_dict = {
	'AB': {'coord_pair': routes[0]},
	'CD': {'coord_pair': routes[1]},
	'AC': {'coord_pair': routes[2]},
	'DB': {'coord_pair': routes[3]},
	'CA': {'coord_pair': routes[4]},
	'BD': {'coord_pair': routes[5]},
	}

	# unpack coordinates and get distance and text from Google Directions API
	for key in routes_dict:
		start, end = routes_dict[key]['coord_pair']
		lat_start, lon_start = start
		lat_end, lon_end = end

		json_temp = 'https://maps.googleapis.com/maps/api/directions/json?origin=%s,%s&destination=%s,%s&mode=driving&key=%s' \
		% (lat_start, lon_start, lat_end, lon_end, Google_key)

		response = json.loads(urlopen(json_temp).read())
		if response['status'] == 'OK':
			routes_dict[key]['distance'] = response['routes'][0]['legs'][0]['distance']['value']
			routes_dict[key]['text'] = response['routes'][0]['legs'][0]['distance']['text']

	return routes_dict

def calc_detour(A, B, C, D):
	""" Given 4 coordinates, calculate the shorter detour between options
		A -> C -> D -> B or
		C -> A -> B -> D """

	routes_dict = create_dist_dict(A, B, C, D)

	# calculate total distance for each option, then subract the direct route to get detour distance
	detour_ACDB = ((routes_dict['AC']['distance'] + routes_dict['CD']['distance'] + routes_dict['DB']['distance']) - routes_dict['AB']['distance']) 
	detour_CABD = ((routes_dict['CA']['distance'] + routes_dict['AB']['distance'] + routes_dict['BD']['distance']) - routes_dict['CD']['distance'])

	# convert distance from meters to unit used by the actual driver
	if routes_dict['AB']['text'].endswith('mi'):
		detour_ACDB *= 0.000621371 # convert meters to miles, if response text shows mi
	else:
		detour_ACDB *= 0.001 # convert meters to km, if response text shows km

	if routes_dict['CD']['text'].endswith('mi'):
		detour_CABD *= 0.000621371
	else:
		detour_CABD *= 0.001

	# print answer
	if detour_ACDB < detour_CABD:
		print 'Driver 1 picks up driver 2 for the shorter detour of %.1f %s.' % (detour_ACDB, routes_dict['AB']['text'][-2:]) 
	elif detour_CABD < detour_ACDB:
		print 'Driver 2 picks up driver 1 for the shorter detour of %.1f %s.' % (detour_CABD, routes_dict['AB']['text'][-2:])
	else:
		print 'The two detours are the same distance of %.1f miles.' % (detour_ACDB)



if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-A', '--A', nargs=2, help='Space separated lat lon for point A')
	parser.add_argument('-B', '--B', nargs=2, help='Space separated lat lon for point B')
	parser.add_argument('-C', '--C', nargs=2, help='Space separated lat lon for point C')
	parser.add_argument('-D', '--D', nargs=2, help='Space separated lat lon for point D')
	parser.add_argument('-i', '--input-file', help='GeoJson formatted list of points')

	args = parser.parse_args()
	if args.input_file:
		with open(args.input_file, 'r') as fp:
			data = json.load(fp)
			A = tuple(data['A']['coordinates'])
			B = tuple(data['B']['coordinates'])
			C = tuple(data['C']['coordinates'])
			D = tuple(data['D']['coordinates'])
	else:
		A = tuple(args.A)
		B = tuple(args.B)
		C = tuple(args.C)
		D = tuple(args.D)

	calc_detour(A, B, C, D)
