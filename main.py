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
		startTime = db.TimeProperty()
		endTime = db.TimeProperty()

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

class Admin(webapp2.RequestHandler):
	def get(self):
		data = {'title': 'Welcome Administrator'}
		doRender(self, 'admin/index.htm', data)
		
	def post(self):
		entity = Admin(
				id = self.request.POST['adminID],
				password = self.request.POST['password'],
				)
		entity.put()
		self.response.status = 302
		self.response.location = '/lecturer/session?session-id=' + entity.id
		
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
				results.append({
					'id':p.id,
					'content':p.content,
					'timestamp':str(p.timestamp),
					'user':p.user,
					'likes':p.likes
					})
		else:
			for p in q.run(limit=int(self.request.get('limit'))):
				results.append({
					'id':p.id,
					'content':p.content,
					'timestamp':str(p.timestamp),
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
				startTime = format(datetime.fromtimestamp(float(self.request.get('startTime'))), '%I:%M'),
				endTime = format(datetime.fromtimestamp(float(self.request.get('endTime'))), '%I:%M')
				)
		entity.put()
		self.response.out.write('created session')


class Lecturer(webapp2.RequestHandler):
	def get(self):
		data = {'title': 'Welcome Lecturer'}
		doRender(self, 'lecturer/index.htm', data)
	def post(self):
		entity = Session(
				id = format(datetime.fromtimestamp(float(self.request.POST['timestamp'])), "%d%b%y") + string.replace(self.request.POST['profName'][:3],' ',''),
				profName = self.request.POST['profName'],
				className = self.request.POST['className'],
				startTime = self.request.POST['startTime'],
				endTime = self.request.POST['endTime']
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

class Student(webapp2.RequestHandler):
	def get(self):
		data = {'title': 'Welcome Student'}
		doRender(self, 'student/index.htm', data)

class ChartData(webapp2.RequestHandler):
	def get(self):
		s = Session.all()
		s.filter('id =', self.request.get('session'))
		results = list()
		for p in s.run(limit=1):
			for time in daterange(p.startTime,p.endTime):
				q = question.all()
				q.filter('session =', p.id)
				q.filter('timestamp >', time)
				q.filter('timestamp <', time + datetime.timedelta(0,60))
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
				results.append({
					'timestamp':time,
					'count_confused':len(qlist) + dcount,
					'count_like':ucount,
					'questions':qlist
					})
			
def daterange(start_date, end_date):
	for n in range(int ((end_date - start_date).minutes)):
		yield start_date + timedelta(n)


class StudentPresentation(webapp2.RequestHandler):
	def get(self):
		data = {
			'title': 'Welcome to ' + self.request.GET['session-id'],
			'session': self.request.GET['session-id']
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
