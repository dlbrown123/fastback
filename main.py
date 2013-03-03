import cgi
import webapp2
import jinja2
import os
import json
import logging
import twilio
import random
from datetime import datetime
import time
from google.appengine.ext import db

random.seed()

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
	likes = db.IntegerProperty()

class MainPage(webapp2.RequestHandler):
	def get(self):
		data = {'title': 'Welcome to Fastback'}
		doRender(self, 'index.htm', data)

class DoFeed(webapp2.RequestHandler):
	def get(self):
		if self.request.get('chart'):
			q = Question.all()
			q.filter('timestamp >',datetime.fromtimestamp(float(self.request.get('timestamp'))))
			self.response.write(q.count())
			return
		q = Question.all()
		q.filter('session =', self.request.get('session'))
		q.order('-timestamp')
		results = list()
		for p in q.run(limit=10):
			results.append({
				'id':p.id,
				'content':p.content,
				'timestamp':format(p.timestamp, "%I:%M"),
				'user':p.user,
				'likes':p.likes
				})
		self.response.out.write(json.dumps(results))
	def post(self):
		if self.request.get('like'):
			q = Question.all()
			q.filter('id =',self.request.get('id'))
			for p in q.run(limit=1):
				if not p.likes:
					p.likes = 0
				p.likes = p.likes + 1
				p.put()
				self.response.write(p.likes)
			self.response.write('likes updated')
			return
		#requires "content" "user" "timestamp" "session"
		entity = Question(
			id = self.request.get('user') + self.request.get('timestamp') + str(random.randrange(0,99)),
			content = self.request.get('content'),
			user = self.request.get('user'),
			timestamp = datetime.time(datetime.fromtimestamp(float(self.request.get('timestamp')))),
			session = self.request.get('session'),
			likes = 0
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
		data = {
			'title': 'Welcome to ' + self.request.GET['session-id'],
			'session': self.request.GET['session-id']
		}
		doRender(self, 'student/main.htm', data)

class PostTest(webapp2.RequestHandler):
	def get(self):
		doRender(self, 'resttest.htm')
	def post(self):
		sid = "AC8a97ca16cd5fa936d40fa0e9f77a47a0"
		token = "1bba88f87630e221c477da45032fd9eb"
		account = twilio.Account(sid, token)
		API_VERSION = '2010-04-01'
		SMS_PATH = '/%s/Accounts/%s/SMS/Messages' % (API_VERSION, sid)
		account.request(path=SMS_PATH,
				method='POST',
				vars={
					'To':'+19196195878',
					'From':'9196480641',
					'Body':self.request.get('msg')
					})
		self.response.out.write('message sent')

class Chart(webapp2.RequestHandler):
	def get(self):
		doRender(self, 'chart.htm')

class Chart(webapp2.RequestHandler):
	def get(self):
		doRender(self, 'chart.htm')

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
	('/chart', Chart),
	('/*', MainPage)
	],
	debug=True)
