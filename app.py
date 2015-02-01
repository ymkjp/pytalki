#!/bin/env python
# -*- coding: utf-8 -*-

import logging

import tornado.ioloop
import tornado.web
import tornado.escape
import tornado.options
from tornado.options import(define, options)
# from tornado_mysql import pools

# Sqlalchemy imports
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import models

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


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db


class MainHandler(BaseHandler):
    def get(self):
        self.write("Hello, world")


class TeachersHandler(BaseHandler):
    def get(self):
        self.write("Hello, world")


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

