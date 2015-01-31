
from sqlalchemy import Column, Integer, String, DateTime, Boolean, DATETIME, Index
from sqlalchemy.schema import Column, ForeignKey, Table, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import INTEGER as Integer

from datetime import datetime

'''
@todo
 1. Pagination
 2. Enum for lang_id, lang_level, lesson_type
'''

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    username = Column(String(30))
    name = Column(String(30), nullable=False)
    email = Column(String(75), nullable=False)
    password = Column(String(128), nullable=False)
    created = Column(DATETIME, default=datetime.now, nullable=False)
    modified = Column(DATETIME, default=datetime.now, nullable=False)

    def __init__(self, username, name):
        self.username = username
        self.name = name
        now = datetime.now()
        self.created = now
        self.modified = now

    def __repr__(self):
        return "<User('%s')>" % (self.name)


class LangLevel(Base):
    __tablename__ = 'lang_level'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    user_id = Column(Integer(unsigned=True), ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE'))
    lang_id = Column(Integer(unsigned=True), index=True, nullable=False)
    lang_level = Column(Integer)

    def __repr__(self):
        return "<LangLevel('user_id:%s,lang_id:%s,lang_level:%s')>" % self.user_id, self.lang_id, self.lang_level


class TeachingLang(Base):
    __tablename__ = 'teaching_lang'
    __table_args__ = (
        (UniqueConstraint('user_id', 'lang_id', name='unique__idx__user_id__lang_id')),
        {'mysql_engine': 'InnoDB'}
    )
    id = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    user_id = Column(Integer(unsigned=True), ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE'))
    lang_id = Column(Integer(unsigned=True), index=True, nullable=False)

    def __repr__(self):
        return "<TeachingLang('%s,%s')>" % self.user_id, self.lang_id


class LearningLang(Base):
    __tablename__ = 'learning_lang'
    __table_args__ = (
        (UniqueConstraint('user_id', 'lang_id', name='unique__idx__user_id__lang_id')),
        {'mysql_engine': 'InnoDB'}
    )
    id = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    user_id = Column(Integer(unsigned=True), ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE'))
    lang_id = Column(Integer(unsigned=True), index=True, nullable=False)

    def __repr__(self):
        return "<LearningLang('%s,%s')>" % self.user_id, self.lang_id

class Course(Base):
    __tablename__ = 'course'
    __table_args__ = (
        {'mysql_engine': 'InnoDB'}
    )
    id = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    user_id = Column(Integer(unsigned=True), ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE'))
    lang_id = Column(Integer(unsigned=True), index=True, nullable=False)
    lesson_type = Column(Integer)
    minutes = Column(Integer)
    itc = Column(Integer)
    session_count = Column(Integer(unsigned=True), default=0)
    rating = Column(Integer(unsigned=True), default=0)

    def __repr__(self):
        return "<Course('%s,%s')>" % self.user_id, self.lang_id


user_table = User.__table__
lang_level_table = LangLevel.__table__
teaching_lang_table = TeachingLang.__table__
learning_lang_table = LearningLang.__table__
course_table = Course.__table__
metadata = Base.metadata


def init_db(engine):
    Base.metadata.create_all(bind=engine)
