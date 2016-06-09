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

import logging
import HTMLParser
import re
import unicodedata as ud
from xml.sax.saxutils import escape
from feed.rss import *
from feed.date.rfc822 import timestamp_from_tf
from feed.date.rfc3339 import tf_from_timestamp
from bottleCBV import BottleView, route
from bottle import request, response, abort
from app.services.feed_service import FeedService
from app.ext.echannel import AtomLink, new_xmldoc_echannel


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
            data = string
            if string is not unicode:
                data = unicode(string)

            return ud.normalize('NFKD', data).encode('ascii', 'xmlcharrefreplace')

        h = HTMLParser.HTMLParser()
        try:
            # host URL
            urlparts = request.urlparts
            host_url = '%s://%s/feeds/%s' % (urlparts.scheme, urlparts.netloc, pkey)

            # get feed data
            cfg = self._app.config
            obj = FeedService.get_feed_activities(db, mc, cfg, pkey)
            activities = obj['activities']
            user_id = obj['user_id']

            # namespaces
            xmldoc, channel = new_xmldoc_echannel()
            xmldoc.root_element.attrs['xmlns:media'] = 'http://search.yahoo.com/mrss/'
            xmldoc.root_element.attrs['xmlns:atom'] = 'http://www.w3.org/2005/Atom'
            xmldoc.root_element.attrs['xmlns:geo'] = 'http://www.w3.org/2003/01/geo/wgs84_pos#'

            # compose items
            channel.title = 'Plus Channel feed'
            channel.description = 'Google+ List of Activities for %s' % obj['name']
            channel.generator = 'Plus Channel %s' % cfg.get('main.version')
            channel.link = 'http://plus.google.com/' + user_id
            channel.docs.text = ''
            channel.atom_link = AtomLink(host_url)
            if 'photo_url' in obj and obj['photo_url'] is not None:
                channel.image = Image(
                    url=obj['photo_url'],
                    title='Plus Channel feed',
                    link='http://plus.google.com/' + user_id,
                    width=cfg.get('feed.photo_size.database'),
                    height=cfg.get('feed.photo_size.database'))
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
                item = Item()
                item.title = check_encoding(title)
                updated = tf_from_timestamp(activity['datePublished'])
                updated = timestamp_from_tf(updated)
                item.pubDate = TextElement('pubDate', updated)

                # process content
                c_content = CDATA()
                c_content.text = check_encoding(content)
                item.description = str(c_content)

                # check image presence
                if 'imageUrl' in activity and activity['imageUrl'] != '':
                    image = TextElement('media:thumbnail')
                    image.attrs['url'] = activity['imageUrl']

                    # check size
                    if 'imageWidth' in activity and 'imageHeight' in activity:
                        image.attrs['width'] = activity['imageWidth']
                        image.attrs['height'] = activity['imageHeight']

                    item.thumbnail = image

                # check coordinates
                if activity['hasCoordinates']:
                    item.lat = TextElement('geo:lat', activity['latitude'])
                    item.long = TextElement('geo:long', activity['longitude'])

                # check link
                if url is None or url == '':
                    url = activity['url']
                item.link = escape(url)
                item.guid = escape(activity['id'])
                item.guid.attrs['isPermaLink'] = 'false'

                channel.items.append(item)

            # return created feed
            response.set_header('content-type', 'application/rss+xml; charset=utf-8')
            return unicode(xmldoc)

        except FeedService.FeedNotFoundException:
            abort(404)

        except FeedService.UserIdNotFoundException:
            abort(410)
