def time_axis_ticks(times):
	import numpy as N
	ticks = N.linspace(0, len(times)-1, num = 9)
	for i in range(len(ticks)-1):
		ticks[i] = ticks[i:i+2].mean()+.5
	ticks = ticks[0:-1]
	labels = []
	for tick in ticks:
		tick = int(tick)
		print tick
		time = times[tick]
		labels.append(timestamp2date(time))
	return ticks, labels

def timestamp2date(time, format='%b %d\n%H:%M:%S'):
	from datetime import datetime
	date = datetime.fromtimestamp(time)
	return date.strftime(format)

def fill_between_vertical(ax, x1, x2, y, **kwargs):
	from matplotlib.patches import Polygon
	# add x,y2 in reverse order for proper polygon filling
	verts = zip(x2,y) + [(x1[i], y[i]) for i in range(len(y)-1,-1,-1)]
	poly = Polygon(verts, **kwargs)
	ax.add_patch(poly)
	#ax.autoscale_view()
	return poly