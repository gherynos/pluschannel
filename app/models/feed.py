"""
Copyright (C) 2012-2016  Luca Zanconato (<luca.zanconato@nharyes.net>)

This file is part of Plus Channel.

Plus Channel is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Plus Channel is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Plus Channel.  If not, see <http://www.gnu.org/licenses/>.
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, func

Base = declarative_base()


class Feed(Base):
    __tablename__ = 'feeds'
    pkey = Column(String, primary_key=True)
    user_id = Column(String)
    inserted = Column(DateTime(), default=func.now())
    photo_url = Column(String)

    def __init__(self, pkey, user_id):
        self.pkey = pkey
        self.user_id = user_id

    def __repr__(self):
        return "<User('%s', '%s')>" % (self.pkey, self.user_id)

    @classmethod
    def get_by_pkey(cls, db, pkey):
        return db.query(cls).filter_by(pkey=pkey).first()

    @classmethod
    def get_by_user_id(cls, db, user_id):
        return db.query(cls).filter_by(user_id=user_id).first()

    def save(self, db):
        db.add(self)
