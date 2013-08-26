import cgi
import urllib

# import gae libs
from google.appengine.api import users
from google.appengine.ext import ndb

# define
MAIN_PAGE_FOOTER_TEMPLATE = """\
		<form action="/sign?%s" method="post">
		<div><textarea name="content" row="3" cols="60"></textarea></div>
		<div><input type="submit" value="Sign Guestbook"></div>
		</form>
		<hr>
		<form> Guestbook name:
		<input value="%s" name="guestbook_name">
		<input type="submit" value="switch">
		</form>

		<a href="%s">%s</a>
		</body>
		</html>
		"""
DEFAULT_GUESTBOOK_NAME="default_guestbook"

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
	""" Make Guestbook Key """
	return ndb.Key('Guestbook',guestbook_name)

class Greeting(ndb.Model):
	""" Model of Greeting """
	author = ndb.UserProperty()
	content = ndb.StringProperty(indexed=False)
	date = ndb.DateTimeProperty(auto_new_add=True)

# Main Page Class
class MainPage(webapp2.RequestHandler):
	def get(self):
		self.response.write('<hrml><body>')
		guestbook_name = self.request.get('guestbook_name',
						  DEFAULT_GUESTBOOK_NAME)

		# Query Part

		greetings_query = Greeting.query(
				ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
		greetings = greetings_query.fetch(10)

		for greeting in greetings:
			if greeting.author:
				self.reponse.write(
						'<b>%s</b>: ' % greeting.author.nickname())
			else:
				self.response.write('Anonymouse: ')
			self.response.write('%s' % cgi.escape(greeting.content))

		if users.get_current_user():
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
		else:
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Login'

		# render forms
		sign_query_params = urllib.urlencode({'guestbook_name':guestbook_name})
		self.response.write(MAIN_PAGE_FOOTER_TEMPLATE % (sign_query_params, cgi.escape(guestbook_name), url, url_linktext))

# post handler
class Guestbook(webapp2.RequestHandler):
	def post(self):
		guestbook.name = self.request.get('guestbook_name',DEFAULT_GUESTBOOK_NAME)
		greeting = Greeting(parent=guestbook_key(guestbook_name))

		if users.get_current_user():
			greeting.author = users.get_current_user()

		greeting.content = self.request.get('content')
		greeting.put()

		query_params = {'guestbook_name':guestbook_name}
		self.redirect('/?' + urllib.urlencode(query_params))

application = webapp2.WSGIApplication([
	('/',MainPage),
	('/sign', Guestbook),
	], debug=True)
