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

import HTMLParser
import logging
import re
import unicodedata as ud
from xml.sax.saxutils import escape

from bottle import request, response, abort
from bottleCBV import BottleView, route
from feedgen.feed import FeedGenerator

from app.ext.geo import GeoExtension
from app.ext.geo_entry import GeoEntryExtension
from app.ext.media import MediaExtension
from app.ext.media_entry import MediaEntryExtension
from app.services.feed_service import FeedService


class Feeds(BottleView):
    @route('/feeds', method='POST')
    def create(self, mc, db):
        response.set_header('content-type', 'application/json')
        data = request.json

        # check User ID parameter
        if data is None or 'user_id' not in data:
            return {'status': 'KO', 'error': 'Please provide the User ID parameter.'}

        try:
            # create feed
            cfg = self._app.config
            feed = FeedService.create_feed(db, mc, cfg, data['user_id'])

            feed['status'] = 'OK'
            return feed

        except FeedService.UserIdNotFoundException:
            return {'status': 'KO', 'error': 'The specified User ID could not be found in Google+.'}

    @route('/feeds/<pkey>', method=['GET'])
    def get(self, mc, db, pkey):
        def check_encoding(string):
            return ud.normalize('NFKD', string).encode('ascii', 'xmlcharrefreplace')

        try:
            # host URL
            urlparts = request.urlparts
            host_url = '%s://%s/feeds/%s' % (urlparts.scheme, urlparts.netloc, pkey)

            # get feed data
            cfg = self._app.config
            obj = FeedService.get_feed_activities(db, mc, cfg, pkey)
            activities = obj['activities']
            user_id = obj['user_id']

            # main element
            channel = FeedGenerator()
            channel.title('Plus Channel feed')
            channel.description('Google+ List of Activities for %s' % obj['name'])
            channel.generator('Plus Channel %s' % cfg.get('main.version'))
            channel.id('http://plus.google.com/' + user_id)
            channel.link(href=host_url, rel='self')
            channel.docs('')
            if 'photo_url' in obj and obj['photo_url'] is not None:
                channel.image(url=obj['photo_url'],
                              title='Plus Channel feed',
                              link='http://plus.google.com/' + user_id,
                              width=str(cfg.get('feed.photo_size.database')),
                              height=str(cfg.get('feed.photo_size.database')))

            # additional namespaces
            channel.register_extension('media', MediaExtension, MediaEntryExtension)
            channel.register_extension('geo', GeoExtension, GeoEntryExtension)

            # compose items
            h = HTMLParser.HTMLParser()
            for activity in activities:

                title = activity['title']
                content = activity['content']
                url = activity['url']

                # check content
                if content is None or content == title:
                    content = ''

                # check title
                if title is None:
                    title = 'notitle'

                # reformat strings
                title = h.unescape(title)
                title = re.sub('<[^>]*>', '', title)
                title = escape(title)
                content = h.unescape(content)
                content = re.sub('<[^>]*>', '', content)
                content = escape(content)

                # log activity
                logging.debug('--- activity ---')
                logging.debug(title)
                logging.debug(content)
                logging.debug(url)
                logging.debug('----------------')

                # create item
                item = channel.add_entry()
                item.title(check_encoding(title))
                item.pubdate(activity['datePublished'])

                # process content
                c_content = check_encoding(content)
                item.description(c_content)
                item.content(content=c_content, type='CDATA')

                # # check image presence
                if 'imageUrl' in activity and activity['imageUrl'] != '':
                    item.media.media_thumbnail_url(activity['imageUrl'])

                    # check size
                    if 'imageWidth' in activity and 'imageHeight' in activity:
                        item.media.media_thumbnail_width(activity['imageWidth'])
                        item.media.media_thumbnail_height(activity['imageHeight'])

                # check coordinates
                if activity['hasCoordinates']:
                    item.geo.geo_lat(activity['latitude'])
                    item.geo.geo_long(activity['longitude'])

                # check link
                if url is None or url == '':
                    url = activity['url']
                item.link(href=escape(url), rel='alternate')
                item.guid(escape(activity['id']))

            # return created feed
            response.set_header('content-type', 'application/rss+xml; charset=utf-8')
            out = unicode(channel.rss_str(pretty=True))
            del channel, activities, user_id, obj
            return out

        except FeedService.FeedNotFoundException:
            abort(404)

        except FeedService.UserIdNotFoundException:
            abort(410)
