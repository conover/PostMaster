from django.conf import settings
import hmac
import logging
import ldap
import base64

def calc_url_mac(url, position, recipient, instance_id):
	mash = ''.join([str(url), str(position), str(recipient), str(instance_id)])
	return hmac.new(settings.SECRET_KEY, mash).hexdigest()

def calc_open_mac(recipient, instance_id):
	mash = ''.join([str(recipient), str(instance_id)])
	return hmac.new(settings.SECRET_KEY, mash).hexdigest()

def calc_unsubscribe_mac(recipient_id):
	mash = ''.join([str(recipient_id)])
	return hmac.new(settings.SECRET_KEY, mash).hexdigest()

def calc_unsubscribe_mac_old(recipient_id, email_id):
	mash = ''.join([str(recipient_id), str(email_id)])
	return hmac.new(settings.SECRET_KEY, mash).hexdigest()

class LDAPHelper(object):
		
	class LDAPHelperException(Exception):
		def __init__(self, error = 'No addtional information'):
			logging.error(': '.join([str(self.__doc__),str(error)]))
			
	class UnableToConnect(LDAPHelperException):
		'''Unable to Connect'''
		pass
	class UnableToBind(LDAPHelperException):
		'''Unable to Bind'''
		pass
	class UnableToSearch(LDAPHelperException):
		'''Unable to Search'''
		pass
	class MultipleUsersFound(LDAPHelperException):
		'''Single search returned more than one'''
		pass
	class NoUsersFound(LDAPHelperException):
		'''Search did not find any users'''
		pass
	class UnexceptedResultForm(LDAPHelperException):
		'''Search result was in an unexpected'''
		pass
	class MissingAttribute(LDAPHelperException):
		'''A requested attribute is missing'''
		pass

	def __init__(self):
		self.connection = LDAPHelper.connect()
		
	@classmethod
	def connect(cls):
		try:
			# TODO - Figure out why we have to ignore the cert check here
			ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
			ldap.set_option(ldap.OPT_REFERRALS, 0)
			return ldap.initialize(settings.LDAP_NET_HOST)
		except ldap.LDAPError, e:
			raise LDAPHelper.UnableToConnect(e)
	
	@classmethod
	def bind(cls,connection,username,password):
		try:
			connection.simple_bind_s(username + settings.LDAP_NET_USER_SUFFIX,password)
		except ldap.LDAPError, e:
			raise LDAPHelper.UnableToBind(e)
	
	@classmethod
	def search_single(cls, *args, **kwargs):
		results = LDAPHelper.search(*args, **kwargs)
		if len(results) == 0:
			raise LDAPHelper.NoUsersFound()
		elif len(results) > 1:
			raise LDAPHelper.MultipleUsersFound()
		else:
			return results[0]

	@classmethod
	def search(cls,connection,filter_params,filter_string='cn=%s'):
		try:
			filter = filter_string % filter_params
			result_id = connection.search(settings.LDAP_NET_BASE_DN,ldap.SCOPE_SUBTREE,filter,None)
		except ldap.LDAPError, e:
			raise LDAPHelper.UnableToSearch(e)
		else:
			results = []
			while 1:
				type, data = connection.result(result_id, 0)
				if (data == []):
					break
				else:
					if type == ldap.RES_SEARCH_ENTRY:
						results.append(data)
			try:
				return list(o[0][1] for o in results)
			except ValueError:
				raise LDAPHelper.UnexpectedResultForm(e)

	@classmethod
	def _extract_attribute(cls,ldap_user,attribute,single=False):
		try:
			if(single):
				return ldap_user[attribute][0]
			else:
				return ldap_user[attribute]

		except KeyError, e:
			raise LDAPHelper.MissingAttribute(e)
		except ValueError, e:
			raise LDAPHelper.MissingAttribute(e)

	@classmethod
	def extract_guid(cls,ldap_user):
		return base64.b64encode(LDAPHelper._extract_attribute(ldap_user,'objectGUID'))
	
	@classmethod
	def extract_firstname(cls,ldap_user):
		return LDAPHelper._extract_attribute(ldap_user,'givenName',single=True)
		
	@classmethod
	def extract_lastname(cls,ldap_user):
		return LDAPHelper._extract_attribute(ldap_user,'sn',single=True)
		
	@classmethod
	def extract_email(cls,ldap_user):
		return LDAPHelper._extract_attribute(ldap_user,'mail',single=True)
	
	@classmethod
	def extract_username(cls,ldap_user):
		return LDAPHelper._extract_attribute(ldap_user,'cn',single=True)
