# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, DateTime, Boolean, DATETIME, Index
from sqlalchemy.schema import Column, ForeignKey, Table, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import TypeDecorator
from sqlalchemy.orm import relation, backref

from faker import Factory

import random
from datetime import datetime
from pprint import pprint

import enum_types

'''

@todo
 1. Pagination
'''

Base = declarative_base()


class EnumType(TypeDecorator):
    """Store IntEnum as Integer"""

    impl = Integer

    def __init__(self, *args, **kwargs):
        self.enum_class = kwargs.pop('enum_class')
        TypeDecorator.__init__(self, *args, **kwargs)

    def process_bind_param(self, value, dialect):
        if value is not None:
            if not isinstance(value, self.enum_class):
                raise TypeError("Value should %s type" % self.enum_class)
            return value.value

    def process_result_value(self, value, dialect):
        if value is not None:
            if not isinstance(value, int):
                raise TypeError("value should have int type")
            return self.enum_class(value)


class User(Base):
    __tablename__ = 'user'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column('id', Integer, primary_key=True)
    username = Column('username', String(30))
    name = Column('name', String(30), nullable=False)
    created = Column('created', DATETIME, default=datetime.now, nullable=False)
    modified = Column('modified', DATETIME, default=datetime.now, nullable=False)

    def __init__(self, username, name):
        self.username = username
        self.name = name
        now = datetime.now()
        self.created = now
        self.modified = now

    def __repr__(self):
        return "<User('%s')>" % self.id


class LangProfile(Base):
    __tablename__ = 'lang_profile'
    __table_args__ = (
        (UniqueConstraint('user_id', 'lang_code', name='unique__idx__user_id__lang_code')),
        Index('idx__lang_code__is_teaching', 'lang_code', 'is_teaching'),
        {'mysql_engine': 'InnoDB'}
    )
    id = Column('id', Integer, primary_key=True)
    user_id = Column('user_id', Integer,
                     ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    lang_code = Column('lang_code', EnumType(enum_class=enum_types.LangCode), index=True, nullable=False)
    lang_level = Column('lang_level', EnumType(enum_class=enum_types.LangLevel))
    is_learning = Column('is_learning', Boolean, index=True, default=False)
    is_teaching = Column('is_teaching', Boolean, index=True, default=False)
    user = relation("User", backref=backref('lang_profile', order_by=id))

    def __repr__(self):
        return "<LangProfile('user_id:%s,lang_code:%s,lang_level:%s')>" % self.user_id, self.lang_code, self.lang_level


class Course(Base):
    __tablename__ = 'course'
    __table_args__ = (
        {'mysql_engine': 'InnoDB'}
    )
    id = Column(Integer, primary_key=True)
    user_id = Column('user_id', Integer,
                     ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    lang_code = Column(EnumType(enum_class=enum_types.LangCode), nullable=False)
    lesson_type = Column(EnumType(enum_class=enum_types.LessonType))
    minutes = Column(Integer)
    itc = Column(Integer)
    session_count = Column(Integer, default=0)
    rating = Column(Integer, default=0)
    user = relation("User", backref=backref('course', order_by=id))

    def __repr__(self):
        return "<Course('%s,%s')>" % self.user_id, self.lang_code


user_table = User.__table__
lang_profile_table = LangProfile.__table__
course_table = Course.__table__
metadata = Base.metadata


def init_db(engine):
    Base.metadata.create_all(bind=engine)

faker = Factory.create()


def insert_dummy_data(session):
    for i in range(20):
        add_one_user(session)


def add_one_user(session):
    user = User(name=faker.name(), username=faker.user_name())
    session.add(user)
    session.commit()

    for i in range(random.randint(1, 3)):
        add_some_lang(session, user)

    session.commit()


def add_some_lang(session, user):
    lang_code = random.choice(list(enum_types.LangCode))
    lang_level = random.choice(list(enum_types.LangLevel))
    is_teaching = faker.boolean() and (3 <= lang_level.value)
    is_learning = faker.boolean() and (lang_level.value <= 6)

    session.add(LangProfile(user_id=user.id,
                            lang_code=lang_code,
                            lang_level=lang_level,
                            is_learning=is_teaching,
                            is_teaching=is_learning,
                            ))

    if is_teaching:
        for i in range(random.randint(1, 5)):
            session.add(Course(user_id=user.id,
                               lang_code=lang_code,
                               lesson_type=random.choice(list(enum_types.LessonType)),
                               minutes=random.randint(1, 12) * 10,
                               itc=random.randint(1, 100) * 10,
                               session_count=random.randint(0, 1000),
                               rating=random.randint(0, 5),
                               ))


