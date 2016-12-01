# Copyright 2015 Vinicius Chiele. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Provides classes for authentication."""

import base64

from flask import request
from werkzeug.http import bytes_to_wsgi, wsgi_to_bytes


def get_authorization_header():
    """
    Return request's 'Authorization:' header as
    a two-tuple of (type, info).
    """
    header = request.environ.get('HTTP_AUTHORIZATION')

    if not header:
        return None

    header = wsgi_to_bytes(header)

    try:
        auth_type, auth_info = header.split(None, 1)
        auth_type = auth_type.lower()
    except ValueError:
        return None

    return auth_type, auth_info


class Authentication(dict):
    """
    A class to hold the authentication data.

    :param str auth_type: The authentication type. e.g: basic, bearer.
    """
    def __init__(self, auth_type, **kwargs):
        super(Authentication, self).__init__(**kwargs)

        self.auth_type = auth_type


class HTTPAuth(object):
    """
    A base class from which all authentication classes should inherit.

    :param str auth_type: The authentication type. e.g: basic, bearer.
    """
    def __init__(self, auth_type):
        self.type = auth_type

    def get_auth(self):
        """
        Get the authentication header.
        :return Authentication: The authentication data or None if it is not present or invalid.
        """
        raise NotImplemented()


class HTTPBasicAuth(HTTPAuth):
    """
    HTTP Basic authentication.
    """
    def __init__(self):
        super(HTTPBasicAuth, self).__init__('Basic')

    def get_auth(self):
        """
        Get the username and password for Basic authentication header.
        :return Authentication: The authentication data or None if it is not present or invalid.
        """
        auth = get_authorization_header()

        if not auth:
            return None

        auth_type, auth_info = auth

        if auth_type != b'basic':
            return None

        try:
            username, password = base64.b64decode(auth_info).split(b':', 1)
        except Exception:
            return None

        return Authentication('basic', username=bytes_to_wsgi(username), password=bytes_to_wsgi(password))
