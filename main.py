import cgi
import webapp2
import jinja2
import os
import json
import logging
from google.appengine.ext import db

jinja_environment = jinja2.Environment(autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))

def doRender(handler, tname='index.htm', values={}):
	temp = jinja_environment.get_template(tname)
	if not temp:
		print "didn't find template"
		return False
	print "here"
	handler.response.out.write(temp.render())
	return True


	
class Session(db.Model):
		id = db.StringProperty()
		profName = db.StringProperty()
		className = db.StringProperty()
		startTime = db.StringProperty()
		endTime = db.StringProperty()
		

class MainPage(webapp2.RequestHandler):
	def get(self):
		doRender(self, 'index.htm')

class Student(webapp2.RequestHandler):
	def get(self):
		doRender(self, 'student.htm')
	
	
class Response(webapp2.RequestHandler):
	def post(self):
		user_input=cgi.escape(self.request.get('Submit'))
		entry =  SearchTerm(term = user_input);
		entry.put();
		
		if user_input in term_dict:
			term = term_dict[user_input]
			q = db.Query(Condition).filter('listing =', term)
			results = q.get()
			results= {'results':results, 'user_input':user_input}
			doRender(self, 'response.htm', results)
			
		elif user_input in slang_dict:
			term = slang_dict[user_input]
			q = db.Query(Condition).filter('listing =', term)
			results = q.get()
			results= {'results':results, 'user_input':user_input}
			doRender(self, 'response.htm', results)
		else:
			template_values = {'user_input':user_input}
			doRender(self, 'not_found.htm', template_values)


#class Search(webapp2.RequestHandler):
#	def get(self):
#		tags = json.dumps(search_data)
#		self.response.out.write(tags)			


app = webapp2.WSGIApplication([('/*', MainPage),
								('/student', Student),
							],
                              debug=True)
