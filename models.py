# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, DateTime, Boolean, DATETIME, Index
from sqlalchemy.schema import Column, ForeignKey, Table, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.dialects.mysql import INTEGER as Integer
from sqlalchemy.types import TypeDecorator
from sqlalchemy.orm import relation, backref

import factory
from factory.alchemy import SQLAlchemyModelFactory
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
    # lang_level = relationship("LangLevel")
    # teaching_lang = relationship("TeachingLang")
    # learning_lang = relationship("LearningLang")
    # course = relationship("Course")

    def __init__(self, username, name):
        self.username = username
        self.name = name
        now = datetime.now()
        self.created = now
        self.modified = now

    def __repr__(self):
        return "<User('%s')>" % self.id


class LangLevel(Base):
    __tablename__ = 'lang_level'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column('id', Integer, primary_key=True)
    user_id = Column('user_id', Integer,
                     ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    lang_code = Column('lang_code', EnumType(enum_class=enum_types.LangCode), index=True, nullable=False)
    lang_level = Column('lang_level', EnumType(enum_class=enum_types.LangLevel))
    user = relation("User", backref=backref('lang_level', order_by=id))

    def __repr__(self):
        return "<LangLevel('user_id:%s,lang_code:%s,lang_level:%s')>" % self.user_id, self.lang_code, self.lang_level


class TeachingLang(Base):
    __tablename__ = 'teaching_lang'
    __table_args__ = (
        (UniqueConstraint('user_id', 'lang_code', name='unique__idx__user_id__lang_code')),
        {'mysql_engine': 'InnoDB'}
    )
    id = Column(Integer, primary_key=True)
    user_id = Column('user_id', Integer,
                     ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    lang_code = Column(EnumType(enum_class=enum_types.LangCode), index=True, nullable=False)
    user = relation("User", backref=backref('teaching_lang', order_by=id))

    def __repr__(self):
        return "<TeachingLang('%s,%s')>" % self.user_id, self.lang_code


class LearningLang(Base):
    __tablename__ = 'learning_lang'
    __table_args__ = (
        (UniqueConstraint('user_id', 'lang_code', name='unique__idx__user_id__lang_code')),
        {'mysql_engine': 'InnoDB'}
    )
    id = Column(Integer, primary_key=True)
    user_id = Column('user_id', Integer,
                     ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    lang_code = Column(EnumType(enum_class=enum_types.LangCode), index=True, nullable=False)
    user = relation("User", backref=backref('learning_lang', order_by=id))

    def __repr__(self):
        return "<LearningLang('%s,%s')>" % self.user_id, self.lang_code


class Course(Base):
    __tablename__ = 'course'
    __table_args__ = (
        {'mysql_engine': 'InnoDB'}
    )
    id = Column(Integer, primary_key=True)
    user_id = Column('user_id', Integer,
                     ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    lang_code = Column(EnumType(enum_class=enum_types.LangCode), index=True, nullable=False)
    lesson_type = Column(EnumType(enum_class=enum_types.LessonType))
    minutes = Column(Integer)
    itc = Column(Integer)
    session_count = Column(Integer, default=0)
    rating = Column(Integer, default=0)
    user = relation("User", backref=backref('course', order_by=id))

    def __repr__(self):
        return "<Course('%s,%s')>" % self.user_id, self.lang_code


user_table = User.__table__
lang_level_table = LangLevel.__table__
teaching_lang_table = TeachingLang.__table__
learning_lang_table = LearningLang.__table__
course_table = Course.__table__
metadata = Base.metadata


def init_db(engine):
    Base.metadata.create_all(bind=engine)

faker = Factory.create()


def insert_dummy_data(session):
    for i in range(10):
        add_one_user(session)


def add_one_user(session):
    user = User(name=faker.name(), username=faker.user_name())
    session.add(user)
    session.commit()

    session.add(LangLevel(user_id=user.id,
                          lang_code=random.choice(list(enum_types.LangCode)),
                          lang_level=random.choice(list(enum_types.LangLevel))))

    session.add(TeachingLang(user_id=user.id,
                             lang_code=random.choice(list(enum_types.LangCode))))

    session.add(LearningLang(user_id=user.id,
                             lang_code=random.choice(list(enum_types.LangCode))))

    session.add(Course(user_id=user.id,
                       lang_code=random.choice(list(enum_types.LangCode)),
                       lesson_type=random.choice(list(enum_types.LessonType)),
                       minutes=random.randint(1, 12) * 10,
                       itc=random.randint(1, 100) * 10,
                       session_count=random.randint(0, 1000),
                       rating=random.randint(0, 5)))
    session.commit()


# class UserFactory(SQLAlchemyModelFactory):
#     class Meta:
#         model = User
#     # id = factory.Sequence(lambda n: n)
#     name = faker.name()
#     username = faker.user_name()
#     # email = faker.safe_email()
#     # password = faker.md5()
#     # lang_level = factory.SubFactory(LangLevelFactory)
#     # teaching_lang = factory.SubFactory(TeachingLang)
#     # learning_lang = factory.SubFactory(LearningLang)
#     # course = factory.SubFactory(Course)
#
#
# class LangLevelFactory(SQLAlchemyModelFactory):
#     class Meta:
#         model = LangLevel
#     # id = factory.Sequence(lambda n: n)
#     user_id = factory.SubFactory(UserFactory)
#     lang_code = random.choice(list(enum_types.LangCode))
#     lang_level = random.choice(list(enum_types.LangLevel))
#
#
# class TeachingLangFactory(SQLAlchemyModelFactory):
#     class Meta:
#         model = TeachingLang
#     # id = factory.Sequence(lambda n: n)
#     user_id = factory.SubFactory(UserFactory)
#     lang_code = random.choice(list(enum_types.LangCode))
#
#
# class LearningLangFactory(SQLAlchemyModelFactory):
#     class Meta:
#         model = LearningLang
#     # id = factory.Sequence(lambda n: n)
#     user_id = factory.SubFactory(UserFactory)
#     lang_code = random.choice(list(enum_types.LangCode))
#
#
# class CourseFactory(SQLAlchemyModelFactory):
#     class Meta:
#         model = Course
#     # id = factory.Sequence(lambda n: n)
#     user_id = factory.SubFactory(UserFactory)
#     lang_code = random.choice(list(enum_types.LangCode))
#     lesson_type = random.choice(list(enum_types.LessonType))
#     minutes = random.randint(1, 12) * 10
#     itc = random.randint(1, 100) * 100
#     session_count = random.randint(0, 1000)
#     rating = random.randint(0, 5)

