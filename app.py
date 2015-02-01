#!/bin/env python
# -*- coding: utf-8 -*-

import logging
from pprint import pprint

import tornado.ioloop
import tornado.web
import tornado.escape
import tornado.options
from tornado.options import(define, options)
# from tornado_mysql import pools

from jinja2 import Environment, FileSystemLoader

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, eagerload

import json

import models
import utils

define("port", default=5000, type=int)
define("debug", default=False, type=bool)
define("sqla_uri", default="")
define("setup", default=False, type=bool)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', MainHandler),
            (r"/teachers", TeachersHandler),
            ]
        settings = dict(
            autoescape="xhtml_escape",
            debug=options.debug,
            )
        tornado.web.Application.__init__(self, handlers, **settings)
        engine = create_engine(options.sqla_uri, convert_unicode=True, echo=options.debug)
        models.init_db(engine)
        self.db = scoped_session(sessionmaker(bind=engine))

        template_loader = FileSystemLoader(searchpath="templates/")
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

        user_list = self.db.query(models.User).options(eagerload('lang_profile')).limit(15).all()
        # todo Fetch by async
        template = self.tpl.get_template('teachers.html')
        template.render()  # returns a string which contains the rendered html
        html_output = template.render(list=user_list, title="Here is your teachers")
        self.write(html_output)


class TeachersHandler(BaseHandler):
    def get(self):
        teachers = self.db.query(models.LangProfile) \
            .options(eagerload('user')) \
            .filter_by(is_teaching=True) \
            .limit(15).all()
        self.write(json.dumps(teachers,
                              cls=utils.recursive_alchemy_encoder(False, ['user']),
                              check_circular=False)
        )


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
