from logging import debug, info, warning
from datetime import datetime, timezone
import requests
import re

from .. import AbstractPollHandler
from data.models import Poll

class PollHandler(AbstractPollHandler):
	_poll_post_url = 'https://youpoll.me'
	_poll_post_headers = {'User-Agent': None}
	_poll_post_data = {'address': '',
	                   'poll-1[question]': None,
	                   'poll-1[option1]': '',
	                   'poll-1[option2]': '',
	                   'poll-1[min]': '1',
	                   'poll-1[max]': 10,
	                   'poll-1[voting-system]': '0',
	                   'poll-1[approval-validation-type]': '0',
	                   'poll-1[approval-validation-value]': '1',
	                   'poll-1[rating]': '',
	                   'voting-limits-dropdown': '3',
			   'captcha-test-checkbox': 'on',
	                   'reddit-link-karma': '0',
	                   'reddit-comment-karma': '0',
	                   'reddit-days-old': '8',
	                   'responses-input': '',
	                   }

	_poll_id_re = re.compile('youpoll.me/(\d+)', re.I)
	_poll_link = 'https://youpoll.me/{id}/'
	_poll_results_link = 'https://youpoll.me/{id}/r'

	def __init__(self):
		super().__init__("youpoll")

	def create_poll(self, title, submit, **kwargs):
		if not submit:
			return None
		#headers = _poll_post_headers
		#headers['User-Agent'] = config.useragent
		data = self._poll_post_data
		data['poll-1[question]'] = title
		#resp = requests.post(_poll_post_url, data = data, headers = headers, **kwargs)
		resp = requests.post(self._poll_post_url, data = data, **kwargs)

		if resp.ok:
			match = self._poll_id_re.search(resp.url)
			return match.group(1)
		else:
			return None

	def get_link(self, poll):
		return self._poll_link.format(id = poll.id)

	def get_results_link(self, poll):
		return self._poll_results_link.format(id = poll.id)

	def get_score(self, poll):
		debug(f"Getting score for show {poll.show_id} / episode {poll.episode}")
		response = self.request(self.get_results_link(poll), html = True)
		value_text = response.find("span", class_="rating-mean-value").text
		num_votes = response.find("span", class_="admin-total-votes").text
		try:
			if int(num_votes) >= 50:
				return float(value_text)
			else:
				info("No value returned because number of votes too low")
				return None
		except ValueError:
			warning(f"Invalid value '{value_text}', no score returned")
			return None
