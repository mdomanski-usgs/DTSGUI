def times_to_dates(times):
	'''Converts a list of unix timestamps to datetime instances'''
	from datetime import datetime
	for time in times:
		time = datetime.fromtimestamp(time)
	return times
	
def rgb_to_hex(rgb_tuple):
	""" convert an (R, G, B) tuple to #RRGGBB """
	rgb_list = [int(i*255) for i in rgb_tuple]
	hexcolor = '#%02x%02x%02x' % tuple(rgb_list)
	return hexcolor