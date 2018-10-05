"""This module houses all of the IDs for the class, and allows the creation of new IDs at will."""
import wx

ID_list = dict()

def set(name):
	"""Sets an ID."""	
	if name in ID_list.keys():	
		raise Exception("The ID for '{}' was already set, and remains unchanged. This might lead to a mismatch.".format(name))
	else: 
		id = wx.NewId()
		ID_list[name] = id
	return ID_list[name]
	
def get(name):
	"""Gets an ID."""
	try:
		return ID_list[name]
	except KeyError:
		print "The name '{}' could not be found in the list of IDs. The ID will be set, but might be mismatched.".format(name)
		return set(name)