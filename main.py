import cgi
import webapp2
import jinja2
import os
import json
import logging
import twilio
import random
import re
from datetime import datetime
from datetime import date
from datetime import timedelta
import time
import string
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

class Admin(db.Model):
		id = db.StringProperty()
		adminName = db.StringProperty()


class Session(db.Model):
		id = db.StringProperty()
		profName = db.StringProperty()
		className = db.StringProperty()
		startTime = db.DateTimeProperty()
		endTime = db.DateTimeProperty()

class Question(db.Model):
	id = db.StringProperty()
	content = db.TextProperty()
	user = db.StringProperty()
	timestamp = db.DateTimeProperty()
	session = db.StringProperty()
	likes = db.IntegerProperty()

class MainPage(webapp2.RequestHandler):
	def get(self):
		data = {'title': 'Welcome to Fastback'}
		doRender(self, 'index.htm', data)

class Admin(webapp2.RequestHandler):
	def get(self):
		data = {'title': 'Welcome Administrator'}
		doRender(self, 'admin/index.htm', data)
		
	def post(self):
		sessions = {'one': '03Mar13DB1', 'two': '03Mar13DB2', 'three': '03Mar13DB3', 'four': '03Mar13EW1', 'five': '03Mar13EW2', 'six': '03Mar13KL1'}
		sessions = {'sessions':sessions}
		doRender(self, 'admin/review.htm', sessions)
		
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
		
class DoFeed(webapp2.RequestHandler):
	def get(self):
		if self.request.get('chart'):
			q = Question.all()
			q.filter('timestamp >',datetime.time(datetime.fromtimestamp(float(self.request.get('timestamp')))))
			self.response.write(q.count())
			return
		q = Question.all()
		q.filter('session =', self.request.get('session'))
		q.order('-timestamp')
		results = list()
		if not self.request.get('limit'):
			for p in q.run():
				results.insert(0, {
					'id':p.id,
					'content':p.content,
					'timestamp':str(p.timestamp),
					'user':p.user,
					'likes':p.likes
					})
		else:
			for p in q.run(limit=int(self.request.get('limit'))):
				results.insert(0, {
					'id':p.id,
					'content':p.content,
					'timestamp':str(p.timestamp.isoformat()),
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
				if p.likes == 2:
					sendText(p.content)
				self.response.write(p.likes)
			self.response.write('likes updated')
			return
		#requires "content" "user" "timestamp" "session"
		entity = Question(
			id = self.request.get('user') + self.request.get('timestamp') + str(random.randrange(0,99)),
			content = self.request.get('content'),
			user = self.request.get('user'),
			timestamp = datetime.fromtimestamp(float(self.request.get('timestamp'))),
			session = self.request.get('session'),
			likes = 1
			)
		entity.put()
		self.response.write('question added')

class DoSessions(webapp2.RequestHandler):
	def get(self):
		q = Session.all()
		results = list()
		for p in q.run(limit=5):
			results.append( {
					'id':p.id,
					'profName':p.profName,
					'className':p.className,
					'startTime':str(p.startTime),
					'endTime':str(p.endTime)
					})
		self.response.out.write(json.dumps(results))
	def post(self):
		#requires "timestamp" "profName" "className" "startTime" "endTime"
		entity = Session(
				id = format(datetime.fromtimestamp(float(self.request.get('timestamp'))), "%d%b%y") + re.sub(r"[ .]",'',self.request.get('profName')[:3]),
				profName = self.request.get('profName'),
				className = self.request.get('className'),
				startTime = datetime.fromtimestamp(float(self.request.get('startTime'))),
				endTime = datetime.fromtimestamp(float(self.request.get('endTime')))
				)
		entity.put()
		self.response.out.write('created session')


class Lecturer(webapp2.RequestHandler):
	def get(self):
		q = Session.all()
		results = list()
		for p in q.run(limit=5):
			results.append( {
					'id':p.id,
					'profName':p.profName,
					'className':p.className,
					'startTime':str(p.startTime),
					'endTime':str(p.endTime)
					})
		data = {
			'title': 'Welcome Lecturer',
			'sessions': results
		}
		doRender(self, 'lecturer/index.htm', data)
	def post(self):
		entity = Session(
				id = format(datetime.fromtimestamp(float(self.request.get('timestamp'))), "%d%b%y") + re.sub(r"[ .]",'',self.request.get('profName')[:3]),
				profName = self.request.POST['profName'],
				className = self.request.POST['className'],
				startTime = datetime.fromtimestamp(float(self.request.POST['startTime'])),
				endTime = datetime.fromtimestamp(float(self.request.POST['endTime']))
				)
		entity.put()
		self.response.status = 302
		self.response.location = '/lecturer/session?session-id=' + entity.id

class LecturerSession(webapp2.RequestHandler):
	def get(self):
		data = {
			'title': 'Session ' + self.request.GET['session-id'],
			'session': self.request.GET['session-id']
		}
		doRender(self, 'lecturer/main.htm', data)

class PostTest(webapp2.RequestHandler):
	def get(self):
		doRender(self, 'resttest.htm')

def sendText(msg):
	sid = "AC8a97ca16cd5fa936d40fa0e9f77a47a0"
	token = "1bba88f87630e221c477da45032fd9eb"
	account = twilio.Account(sid, token)
	API_VERSION = '2010-04-01'
	SMS_PATH = '/%s/Accounts/%s/SMS/Messages' % (API_VERSION, sid)
	account.request(path=SMS_PATH,
		method='POST',
		vars={
			'To':'+19194549203',
			'From':'9196480641',
			'Body':msg
			})

class Student(webapp2.RequestHandler):
	def get(self):
		data = {'title': 'Welcome Student'}
		doRender(self, 'student/index.htm', data)

class ChartData(webapp2.RequestHandler):
	def get(self):
		s = Session.all()
		s.filter('id =', self.request.get('session'))
		results = list()
		for p in s.run():
			for time in daterange(p.startTime,p.endTime):
				q = Question.all()
				q.filter('session =', p.id)
				q.filter('timestamp >', time)
				q.filter('timestamp <', time + timedelta(0,60))
				qlist = list()
				dcount = 0
				ucount = 0
				for question in q.run():
					if question.content == '?':
						dcount += 1
					elif question.content == '!':
						ucount += 1
					else:
						qlist.append(question.content)
						dcount = question.likes
				results.append({
					'timestamp':str(time.isoformat()),
					'count_confused':dcount,
					'count_like':ucount,
					'questions':qlist
					})
		self.response.write(json.dumps(results))
			
def daterange(start_date, end_date):
	for n in range(int ((end_date - start_date).total_seconds()/60)):
		yield start_date + timedelta(0,n*60)


class StudentPresentation(webapp2.RequestHandler):
	def get(self):
		data = {
			'title': 'Welcome to ' + self.request.GET['session-id'],
			'session': self.request.GET['session-id'],
			'user': 'anon' + str(random.randrange(0, 1000))
		}
		doRender(self, 'student/main.htm', data)

app = webapp2.WSGIApplication([
	('/test', PostTest),
	('/session', DoSessions),
	('/feed', DoFeed),
	('/student', Student),
	('/student/presentation', StudentPresentation),
	('/lecturer', Lecturer),
	('/lecturer/session', LecturerSession),
	('/createData', CreateData),
	('/chart', Chart),
	('/chartData', ChartData),
	('/*', MainPage),
	('/admin', Admin)
	],
	debug=True)
