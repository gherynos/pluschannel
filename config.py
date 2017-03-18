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

import bottle.ext.memcache
import yaml
from bottle import Bottle, static_file
from bottle import response, jinja2_template as template
from bottle_sqlalchemy import Plugin as bottleSQLAlchemyPlugin
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from app.controllers.feeds import Feeds
from app.controllers.home import Home

with open('config.yaml', 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

    # Bottle app
    app = Bottle()
    app.config.load_dict(cfg)

    # templates
    bottle.TEMPLATE_PATH = 'app/templates',

    # Memcached
    mc_plugin = bottle.ext.memcache.MemcachePlugin(servers=[cfg['main']['memchache_server']])
    app.install(mc_plugin)

    # DB
    Base = declarative_base()
    engine = create_engine(cfg['main']['db_url'])
    plugin = bottleSQLAlchemyPlugin(
        engine,
        Base.metadata,
        keyword='db',
        create=False,
        commit=True,
        use_kwargs=False
    )
    app.install(plugin)

    # Common headers for responses
    def set_common_headers(res):
        res.headers['X-Frame-Options'] = 'SAMEORIGIN'
        res.headers['X-XSS-Protection'] = '1; mode=block'
        res.headers['X-Content-Type-Options'] = 'nosniff'


    @app.hook('after_request')
    def common_headers():
        set_common_headers(response)


    # serve IMG files
    @app.route('/img/<filepath:path>')
    def serve_static_img(filepath):
        res = static_file(filepath, root='app/static/img')
        set_common_headers(res)
        return res


    # serve JS files
    @app.route('/js/<filepath:path>')
    def serve_static_js(filepath):
        res = static_file(filepath, root='app/static/js')
        set_common_headers(res)
        return res


    # serve TPL files
    @app.route('/tpl/<filepath:path>')
    def serve_static_tpl(filepath):
        res = static_file(filepath, root='app/static/tpl')
        set_common_headers(res)
        return res


    # serve CSS files
    @app.route('/css/<filepath:path>')
    def serve_static_css(filepath):
        res = static_file(filepath, root='app/static/css')
        set_common_headers(res)
        return res


    # serve FONTS files
    @app.route('/fonts/<filepath:path>')
    def serve_static_fonts(filepath):
        res = static_file(filepath, root='app/static/fonts')
        set_common_headers(res)
        return res


    # serve FAVICON file
    @app.route('/favicon.ico')
    def serve_static_favicon():
        res = static_file('favicon.ico', root='app/static/img/ico')
        set_common_headers(res)
        return res


    # serve ROBOTS file
    @app.route('/robots.txt')
    def serve_static_robots():
        res = static_file('robots.txt', root='app/static')
        set_common_headers(res)
        return res


    # serve other static files
    @app.route('/static/<filepath:path>')
    def serve_static(filepath):
        res = static_file(filepath, root='app/static')
        set_common_headers(res)
        return res


    # custom errors
    @app.error(400)
    def error400(err):
        set_common_headers(response)
        return template('errors/400.html', dict())


    @app.error(401)
    def error401(err):
        set_common_headers(response)
        return template('errors/401.html', dict())


    @app.error(404)
    def error404(err):
        set_common_headers(response)
        return template('errors/404.html', dict())


    @app.error(410)
    def error410(err):
        set_common_headers(response)
        return template('errors/410.html', dict())


    @app.error(500)
    def error500(err):
        set_common_headers(response)
        return template('errors/500.html', dict())


    # register controllers
    Home.register(app)
    Feeds.register(app)
