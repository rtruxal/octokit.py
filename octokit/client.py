# -*- coding: utf-8 -*-

"""
octokit.client
~~~~~~~~~~~~~~

This module contains the main Client class for octokit.py
"""

# https://code.google.com/p/uri-templates/wiki/Implementations

from .exceptions import handle_status
from .ratelimit import RateLimit
from .resources import Resource

import requests

class BaseClient(Resource):
  def __init__(self, session=requests.Session(), api_endpoint='https://api.github.com', **kwargs):
    self.session = session
    self.url = api_endpoint
    self.schema = {}
    self.name = 'Client'
    self.auto_paginate = False

    self.session.hooks = dict(response=self.response_callback)
    for key in kwargs:
      setattr(self.session, key, kwargs[key])

  def response_callback(self, r, *args, **kwargs):
    self.last_response = r
    data = r.json() if r.text != "" else {}
    handle_status(r.status_code, data)
    # TODO (howei): perhaps we could auto-paginate requests here

  def paginate(self, url, *args, **kwargs):
    session = self.session
    params = {}
    if 'per_page' in kwargs:
      params['per_page'] = kwargs['per_page']
      del kwargs['per_page']
    elif self.auto_paginate:
      # if per page is not defined, default to 100 per page
      params['per_page'] = 100

    if 'page' in kwargs:
      params['page'] = kwargs['page']
      del kwargs['page']

    kwargs['params'] = params
    resource = Resource(session, url=url, name=url)
    data = list(resource.get(*args, **kwargs).schema)

    if self.auto_paginate:
      while 'next' in resource.rels and self.rate_limit.remaining > 0:
        resource = resource.rels['next']
        data.extend(list(resource.get().schema))

    return Resource(session, schema=data, url=self.url, name=self.name)

class Client(RateLimit, BaseClient):
  """The main class for using octokit.py.

  This class accepts as arguments any attributes that can be set on a
  Requests.Session() object. After instantiation, the session may be modified
  by accessing the `session` attribute.

  Example usage:

    >>> client = octokit.Client(auth = ('mastahyeti', 'oauth-token'))
    >>> client.session.proxies = {'http': 'foo.bar:3128'}
    >>> client.current_user.login
    'mastahyeti'
  """
  pass
