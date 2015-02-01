# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, DateTime, Boolean, DATETIME, Index
from sqlalchemy.schema import Column, ForeignKey, Table, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, backref

from faker import Factory

import random
from datetime import datetime

import enum_types
import utils

'''

@todo
 1. Pagination
'''

Base = declarative_base()


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

    # def __repr__(self):
    #     return "<User('id:%s, name:%s')>" % self.id, self.name


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
    lang_code = Column('lang_code', utils.EnumType(enum_class=enum_types.LangCode), index=True, nullable=False)
    lang_level = Column('lang_level', utils.EnumType(enum_class=enum_types.LangLevel))
    is_learning = Column('is_learning', Boolean, index=True, default=False)
    is_teaching = Column('is_teaching', Boolean, index=True, default=False)
    user = relation("User", backref=backref('lang_profile', order_by=id))

    # def __repr__(self):
    #     return "<LangProfile('user_id:%s,lang_code:%s,lang_level:%s')>" % (
    #         self.user_id, self.lang_code, self.lang_level)


class Course(Base):
    __tablename__ = 'course'
    __table_args__ = (
        {'mysql_engine': 'InnoDB'}
    )
    id = Column(Integer, primary_key=True)
    user_id = Column('user_id', Integer,
                     ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    lang_code = Column(utils.EnumType(enum_class=enum_types.LangCode), nullable=False)
    lesson_type = Column(utils.EnumType(enum_class=enum_types.LessonType))
    minutes = Column(Integer)
    itc = Column(Integer)
    session_count = Column(Integer, default=0)
    rating = Column(Integer, default=0)
    user = relation("User", backref=backref('course', order_by=id))

    # def __repr__(self):
    #     return "<Course('%s,%s')>" % self.user_id, self.lang_code


user_table = User.__table__
lang_profile_table = LangProfile.__table__
course_table = Course.__table__
metadata = Base.metadata


def init_db(engine):
    Base.metadata.create_all(bind=engine)

faker = Factory.create()


def insert_dummy_data(session):
    for i in range(100):
        add_one_user(session)

    session.commit()


def add_one_user(session):
    user = User(name=faker.name(), username=faker.user_name())
    session.add(user)
    session.commit()

    # Every user has one native language at least
    lang_code_list = random.sample(list(enum_types.LangCode), random.randint(1, 3))
    add_lang(session, user, lang_code_list.pop(), enum_types.LangLevel.Native)
    for lang_code in lang_code_list:
        add_lang(session, user, lang_code, random.choice(list(enum_types.LangLevel)))


def add_lang(session, user, lang_code, lang_level):
    is_teaching = faker.boolean() and (5 <= lang_level.value)
    is_learning = faker.boolean() and (lang_level.value <= 6)

    session.add(LangProfile(user_id=user.id,
                            lang_code=lang_code,
                            lang_level=lang_level,
                            is_learning=is_learning,
                            is_teaching=is_teaching,
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


