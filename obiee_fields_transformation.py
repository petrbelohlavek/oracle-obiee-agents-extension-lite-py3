class FieldsTransformation(object):
	def __init__(self, field_enclosed='"', fields_terminated='\t'):
		self.fields_enclosed = field_enclosed
		self.fields_terminated = fields_terminated

	def get_field_encl(self, field):		
		return '{}{}{}'.format(self.fields_enclosed, field, self.fields_enclosed)

	def get_field_encl_newln(self, field):
		return '{}{}{}\n'.format(self.fields_enclosed, field, self.fields_enclosed)

	def get_field_encl_term(self, field):		
		return '{}{}{}{}'.format(self.fields_enclosed, field, self.fields_enclosed, self.fields_terminated)
