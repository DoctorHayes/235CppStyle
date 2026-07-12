
def check_filename_spaces(self, filename):
	"""
	Error if there is a space in the filename
	"""
	if filename.find(' ') >= 0:
		better = filename.replace(' ', '_')  # suggest replacing spaces with underscores
		self.add_error(label="FILENAME_SPACES", line = 0, data={'filename': filename, 'suggestion': better})