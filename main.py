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
	handler.response.out.write(temp.render(values))
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
	user = db.StringProperty()
	timestamp = db.TimeProperty()
	session = db.StringProperty()

class MainPage(webapp2.RequestHandler):
	def get(self):
		data = {'title': 'Welcome to Fastback'}
		doRender(self, 'index.htm', data)

class DoFeed(webapp2.RequestHandler):
	def get(self):
		if self.request.get('chart'):
			q = Question.all()
			q.filter('timestamp >',datetime.fromtimestamp(float(self.request.get('timestamp'))))
			q.order('-timestamp')
			results = list()
			for p in q.run():
				results.append()
			return
		q = Question.all()
		results = list()
		for p in q.run():
			results.append({
				'id':p.id,
				'content':p.content,
				'timestamp':format(p.timestamp, "%I:%M"),
				'user':p.user
				})
		self.response.out.write(json.dumps(results))
	def post(self):
		#requires "content" "user" and "session"
		entity = Question(
			id = self.request.get('user') + self.request.get('timestamp'),
			content = self.request.get('content'),
			user = self.request.get('user'),
			timestamp = datetime.fromtimestamp(float(self.request.get('timestamp'))),
			session = self.request.get('session')
			)
		entity.put()

class DoSessions(webapp2.RequestHandler):
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
	def post(self):
		#requires "timestamp" "profName" "className" "startTime" "endTime"
		entity = Session(
				id = format(datetime.fromtimestamp(float(self.request.get('timestamp'))), "%d%b%y") + string.replace(self.request.get('profName')[:3],' ',''),
				profName = self.request.get('profName'),
				className = self.request.get('className'),
				startTime = self.request.get('startTime'),
				endTime = self.request.get('endTime')
				#startTime = format(datetime.fromtimestamp(float(self.request.get('startTime'))), '%I:%M'),
				#endTime = format(datetime.fromtimestamp(float(self.request.get('endTime'))), '%I:%M')
				)
		entity.put()
		self.response.out.write('created session')

class Student(webapp2.RequestHandler):
	def get(self):
		data = {'title': 'Welcome Student'}
		doRender(self, 'student/index.htm', data)

class StudentPresentation(webapp2.RequestHandler):
	def get(self):
		data = {'title': 'Welcome to ' + self.request.GET['session-id']}
		doRender(self, 'student/main.htm', data)

class PostTest(webapp2.RequestHandler):
	def get(self):
		doRender(self, 'resttest.htm')
	def post(self):
		self.response.out.write('nothing yet')

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
	('/test', PostTest),
	('/session', DoSessions),
	('/feed', DoFeed),
	('/student', Student),
	('/student/presentation', StudentPresentation),
	('/createData', CreateData),
	('/*', MainPage)
	],
	debug=True)
