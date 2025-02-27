#! /usr/bin/env python
# Newspipe - A web news aggregator.
# Copyright (C) 2010-2025 Cédric Bonhomme - https://www.cedricbonhomme.org
#
# For more information: https://github.com/cedricbonhomme/newspipe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 0.5 $"
__date__ = "$Date: 2013/11/05 $"
__revision__ = "$Date: 2022/01/02 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "GPLv3"

import re
from datetime import datetime

from flask_login import UserMixin
from sqlalchemy.orm import validates
from werkzeug.security import check_password_hash

from newspipe.bootstrap import db
from newspipe.models.bookmark import Bookmark
from newspipe.models.category import Category
from newspipe.models.feed import Feed
from newspipe.models.right_mixin import RightMixin


class User(db.Model, UserMixin, RightMixin):
    """
    Represent a user.
    """

    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(), unique=True)
    pwdhash = db.Column(db.String())
    external_auth = db.Column(db.String(), default="", nullable=True)

    automatic_crawling = db.Column(db.Boolean(), default=True)

    is_public_profile = db.Column(db.Boolean(), default=False)
    bio = db.Column(db.String(5000), default="")
    webpage = db.Column(db.String(), default="")
    mastodon = db.Column(db.String(500), default="")
    github = db.Column(db.String(39), default="")
    linkedin = db.Column(db.String(30), default="")

    date_created = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

    # user rights
    is_active = db.Column(db.Boolean(), default=False)
    is_admin = db.Column(db.Boolean(), default=False)
    is_api = db.Column(db.Boolean(), default=False)

    # relationships
    categories = db.relationship(
        "Category",
        backref="user",
        cascade="all, delete-orphan",
        foreign_keys=[Category.user_id],
    )
    feeds = db.relationship(
        "Feed",
        backref="user",
        cascade="all, delete-orphan",
        foreign_keys=[Feed.user_id],
    )
    bookmarks = db.relationship(
        "Bookmark",
        backref="user",
        cascade="all, delete-orphan",
        foreign_keys=[Bookmark.user_id],
    )

    @staticmethod
    def _fields_base_write():
        return {"login", "password"}

    @staticmethod
    def _fields_base_read():
        return {"date_created", "last_seen"}

    @staticmethod
    def make_valid_nickname(nickname):
        return re.sub("[^a-zA-Z0-9_-]", "", nickname)

    def get_id(self):
        """
        Return the id of the user.
        """
        return self.id

    @validates("bio")
    def validates_bio(self, key, value):
        assert len(value) <= 5000, AssertionError("maximum length for bio: 5000")
        return value.strip()

    @validates("github")
    def validates_github(self, key: str, value: str) -> str:
        assert 0 <= len(value) <= 39, AssertionError("Maximum length for GitHub: 39")
        if value.strip():
            github_regex = r"^[a-zA-Z\d](?:[a-zA-Z\d]|-(?=[a-zA-Z\d])){0,38}$"
            assert re.match(github_regex, value) is not None, AssertionError(
                "Invalid GitHub username."
            )
        return value

    @validates("linkedin")
    def validates_linkedin(self, key: str, value: str) -> str:
        assert 0 <= len(value) <= 30, AssertionError("Maximum length for LinkedIn: 30")
        if value.strip():
            linkedin_regex = r"^[a-zA-Z\d](?:[a-zA-Z\d-]{0,28}[a-zA-Z\d])?$"
            assert re.match(linkedin_regex, value) is not None, AssertionError(
                "Invalid LinkedIn username."
            )
        return value

    def check_password(self, password):
        """
        Check the password of the user.
        """
        return check_password_hash(self.pwdhash, password)

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return "<User %r>" % (self.nickname)
