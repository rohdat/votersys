# """

# Voter system

# dbs?

# -
# -
# -



# Charting? 

# -
# -
# -


# html get form and post form

# -
# -
# -


# -> What do you want to vote on?
# -> How many votes are allowed? Option to limit # of voters
# -> Password for voting - signup by email? by phone num? 
# -> Do we text users?
# """

#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import cgi
import jinja2 
import time
from google.appengine.ext import db
from google.appengine.ext import ndb
import logging
import json
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


template_dir = os.path.join(os.path.dirname(__file__), 'static')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

def users_key(group = 'default'):
    return Key.from_path('users', group)

class Topic(ndb.Model):
	name = ndb.StringProperty(required=True)
	pro   = ndb.IntegerProperty()
	con   = ndb.IntegerProperty()
	created = ndb.DateTimeProperty(auto_now_add=True)
	votermax = ndb.IntegerProperty()
	def get_total_votes():
		return pro + con

	@classmethod
	def create(cls, name, votermax):
		return Topic(name=name, votermax=votermax, pro=0, con= 0)


	def get_result():
		if pro > con:
			return "Y"
		elif pro == con:
			return "T"
		elif pro < con:
			return "N"

class Handler (webapp2.RequestHandler):
    def write (self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class VoterHandler(Handler):

	def get(self):
		self.render("voterfront.html")

	def post(self):
		choice = self.request.get("choice")
		logging.error("CHOICE=%s"%choice)
		if choice == "newvote":
			self.redirect ("/newvote")
		elif choice == "getold":
			self.redirect ("/")
		else:
			self.redirect("/")
			self.write("Please select one")




class NewVoteHandler(Handler):

	def get(self):
		self.render("newvote.html")


	def post(self):
		topic = self.request.get("topic")
		votermax = int(self.request.get("votermax"))
		t = Topic(name=topic, votermax=votermax, pro=0, con=0)
		t_key = t.put()
		t_id = t_key.urlsafe()
		logging.error("Key=%s"%t_id)
		self.redirect("/newvote/%s"%t_id)

class VotePageHandler(Handler):

	def get_item(self,urlkey):
		return ndb.Key(urlsafe=urlkey).get()

	def get(self, urlkey):
		t = self.get_item(urlkey)
		self.render("votepage.html", votesfor= t.pro, votesagainst = t.con)

	def post(self, urlkey):
		t = self.get_item(urlkey)
		choice = self.request.get("choice")
		if choice == "yes":
			t.pro = int(t.pro) + 1
		elif choice == "no":
			t.con = int(t.con) + 1
		t.put()
		self.render("votepage.html", votesfor= t.pro, votesagainst = t.con)
		self.write("Thank you for voting! Every vote counts!")
