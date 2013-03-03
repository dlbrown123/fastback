import cgi
import webapp2
import jinja2
import os
import json
import logging
from datetime import datetime
import time
from google.appengine.ext import db

jinja_environment = jinja2.Environment(autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))

def doRender(handler, tname='index.htm', values={}):
	temp = jinja_environment.get_template(tname)
	if not temp:
		return False
	handler.response.out.write(temp.render())
	return True
	
class Session(db.Model):
		id = db.StringProperty()
		profName = db.StringProperty()
		className = db.StringProperty()
		startTime = db.StringProperty()
		endTime = db.StringProperty()

class Question(db.Model):
	id = db.StringProperty()
	content = db.TextProperty()
	timestamp = db.TimeProperty()

class MainPage(webapp2.RequestHandler):
	def get(self):
		self.response.out.write('main page')

class DoFeed(webapp2.RequestHandler):
	def get(self):
		q = Question.all()
		results = list()
		for p in q.run():
			results.append({
				'id':p.id,
				'content':p.content,
				'timestamp':format(p.timestamp, "%I:%M")
				})
		self.response.out.write(json.dumps(results))

class GetSessions(webapp2.RequestHandler):
	def get(self):
		q = Session.all()
		results = list()
		for p in q.run(limit=5):
			results.append( {
					'id':p.id,
					'profName':p.profName,
					'className':p.className,
					'startTime':p.startTime,
					'endTime':p.endTime
					})
		self.response.out.write(json.dumps(results))
		#doRender(self, 'index.htm')

class Student(webapp2.RequestHandler):
	def get(self):
		self.response.out.write('no page here yet')
		#doRender(self, 'student.htm')

class CreateData(webapp2.RequestHandler):
	def get(self):
		entry = Question(
				id = '1',
				content = 'This is some sample text for a question.',
				timestamp = datetime.time(datetime.now())
				)
		entry.put()
		self.response.out.write('created')

app = webapp2.WSGIApplication([
	('/session', GetSessions),
	('/feed', DoFeed),
	('/student', Student),
	('/createData', CreateData),
	('/*', MainPage)
	],
	debug=True)
