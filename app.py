#!/bin/env python
# -*- coding: utf-8 -*-


import os
import logging
from pprint import pprint

import tornado.ioloop
import tornado.web
import tornado.escape
import tornado.options
from tornado.options import(define, options)

from jinja2 import Environment, FileSystemLoader

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, eagerload
import pycountry
import json

import models
import utils
import enum_types

define("port", default=5000, type=int)
define("debug", default=False, type=bool)
define("sqla_uri", default="", help="database resource like: 'mysql://username:password@localhost/db_name'")
define("setup", default=False, type=bool, help="setup dummy data")


class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            autoescape="xhtml_escape",
            debug=options.debug,
            # static_path="statics"
            static_path=os.path.join(os.path.dirname(__file__), "statics")
        )
        handlers = [
            (r'/', MainHandler),
            (r"/teachers", TeachersHandler),
            (r"/statics/(.*)", tornado.web.StaticFileHandler, dict(path=settings['static_path'])),
        ]
        tornado.web.Application.__init__(self, handlers, **settings)
        engine = create_engine(options.sqla_uri, convert_unicode=True, echo=options.debug)
        models.init_db(engine)
        self.db = scoped_session(sessionmaker(bind=engine))

        template_loader = FileSystemLoader(searchpath=os.path.join(os.path.dirname(__file__), "templates/"))
        self.tpl = Environment(loader=template_loader)


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    @property
    def tpl(self):
        return self.application.tpl


class MainHandler(BaseHandler):
    def get(self):

        language_list = [{"name": lang.name, "code": lang.alpha2} for lang
                         in pycountry.languages if hasattr(lang, 'alpha2')]

        template = self.tpl.get_template('teachers.html')
        template.render()  # returns a string which contains the rendered html
        html_output = template.render(language_list=language_list,
                                      title="Search your teacher or student")
        self.write(html_output)


class TeachersHandler(BaseHandler):
    def get(self):
        lang_code = self.get_argument('lang_code')
        user_type = self.get_argument('user_type')  # 'teacher' or 'student' otherwise tornado.web.MissingArgumentError

        user = models.User
        lang_profile = models.LangProfile

        user_list = self.db.query(user) \
            .options(eagerload('lang_profile')) \
            .filter(user.id == lang_profile.user_id) \
            .filter(lang_profile.lang_code == enum_types.LangCode[lang_code]) \
            .filter(lang_profile.is_teaching if user_type == "teacher" else lang_profile.is_learning) \
            .limit(15).all()

        self.write(json.dumps(user_list,
                              cls=utils.recursive_alchemy_encoder(False, ['lang_profile']),
                              check_circular=False))


def main():
    tornado.options.parse_config_file('app.conf')
    tornado.options.parse_command_line()
    app = Application()
    if options.setup:
        models.insert_dummy_data(app.db)
    app.listen(options.port)
    logging.debug('run on port %d in %s mode' % (options.port, options.logging))
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
