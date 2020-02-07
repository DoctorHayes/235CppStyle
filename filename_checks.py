import re
from werkzeug.utils import secure_filename

def check_filename_spaces(self, filename):
	"""
	Error if there is a space in the filename
	"""
	if filename.find(' ') >= 0:
		better = secure_filename(filename) # removes spaces and other things.
		self.add_error(label="FILENAME_SPACES", line = 0, data={'filename': filename, 'suggestion': better})