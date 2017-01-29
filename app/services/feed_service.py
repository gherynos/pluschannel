"""
Copyright (C) 2012-2017  Luca Zanconato (<luca.zanconato@nharyes.net>)

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

import random
import string

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials

from app.models.feed import Feed


class FeedService:
    MEMCACHE_KEY = 'plusc_feed_%s'
    credentials = None

    def __init__(self):
        pass

    @classmethod
    def _get_plus_service(cls, credentials_file):

        if not cls.credentials:
            cls.credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, [
                'https://www.googleapis.com/auth/plus.login'])
        http_auth = cls.credentials.authorize(Http())

        return build('plus', 'v1', http=http_auth, cache_discovery=False)

    @classmethod
    def create_feed(cls, db, mc, cfg, user_id):
        def get_random_key():
            return ''.join(
                random.SystemRandom().choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in
                range(12))

        try:
            # get user details from Google Plus
            service = cls._get_plus_service(cfg.get('feed.credentials_file'))
            person = service.people().get(userId=user_id).execute()

            # change photo size
            photo_url_site = person['image']['url']
            photo_url_db = person['image']['url']
            idx = photo_url_site.index('?')
            if idx != -1:
                photo_url_site = '%s?sz=%s' % (photo_url_site[:idx], cfg.get('feed.photo_size.website'))
                photo_url_db = '%s?sz=%s' % (photo_url_db[:idx], cfg.get('feed.photo_size.database'))

            # check feed existence
            uid = person['id']
            feed = Feed.get_by_user_id(db, uid)
            if not feed:
                # create a new feed
                rnd_key = get_random_key()
                while Feed.get_by_pkey(db, rnd_key):
                    rnd_key = get_random_key()
                feed = Feed(rnd_key, uid)
                feed.save(db)

            else:
                mc.delete(cls.MEMCACHE_KEY % feed.pkey)

            # update photo
            feed.photo_url = photo_url_db
            feed.save(db)

            return {'pkey': feed.pkey, 'photo': photo_url_site, 'name': person['displayName']}

        except HttpError as e:
            if e.resp.status == 404:
                raise cls.UserIdNotFoundException
            raise e

    @classmethod
    def get_feed_activities(cls, db, mc, cfg, pkey):
        def process_activity_data(atv):
            # check re-shared post
            title = ''
            content = ''
            url = ''
            if atv['actorId'] != user_id:
                # check attachment
                if atv['hasAttachment']:
                    # check comment
                    if atv['hasComment']:
                        if 'comment' in atv:
                            title = atv['comment']
                        if 'attachmentTitle' in atv:
                            content = atv['attachmentTitle']
                        if 'attachmentUrl' in atv:
                            url = atv['attachmentUrl']

                    else:
                        if 'attachmentTitle' in atv:
                            title = atv['attachmentTitle']
                        if 'attachmentContent' in atv:
                            content = atv['attachmentContent']
                        if 'attachmentUrl' in atv:
                            url = atv['attachmentUrl']
                else:
                    # set only title and content
                    if 'title' in atv and atv['title'] != '':
                        title = atv['title']
                    if 'content' in atv and atv['content'] != '':
                        content = atv['content']

            else:
                if 'title' in atv and atv['title'] != '':
                    title = atv['title']
                elif atv['hasAttachment'] and 'attachmentTitle' in atv:
                    title = atv['attachmentTitle']

                if 'content' in atv and atv['content'] != '':
                    content = atv['content']
                elif atv['hasAttachment'] and 'attachmentContent' in atv:
                    content = atv['attachmentContent']

                if atv['hasAttachment'] and 'attachmentUrl' in atv:
                    url = atv['attachmentUrl']

            # update activity
            atv['title'] = title
            atv['content'] = content
            if url is not None and url != '':
                atv['url'] = url

        # check memcache for existing value
        m_key = cls.MEMCACHE_KEY % pkey
        feed = mc.get(m_key)
        if not feed:
            # load feed from DB
            db_feed = Feed.get_by_pkey(db, pkey)
            if not db_feed:
                db_feed = 404
            mc.set(m_key, db_feed)
            feed = db_feed

        if feed == 404:
            raise cls.FeedNotFoundException()
        user_id = feed.user_id

        try:
            # get user activities
            service = cls._get_plus_service(cfg.get('feed.credentials_file'))
            obj = service.activities().list(userId=user_id, collection='public', maxResults='5').execute()

        except HttpError as e:
            if e.resp.status == 404:
                raise cls.UserIdNotFoundException
            raise e

        # parse activities
        activities = []
        name = None
        for item in obj.get('items'):
            # compose activity
            activity = {'id': item['id'], 'url': item['url'], 'title': item['title'],
                        'content': item['object']['content'],
                        'datePublished': item['published'], 'actorId': item['actor']['id'],
                        'hasAttachment': 'attachments' in item['object'] and len(item['object']['attachments']) > 0,
                        'hasComment': 'annotation' in item}

            # check annotation
            if activity['hasComment']:
                activity['comment'] = item['annotation']

            # check geocode
            if 'geocode' in item:
                c = item['geocode'].split(' ')

                activity['hasCoordinates'] = True
                activity['latitude'] = c[0]
                activity['longitude'] = c[1]

            else:
                activity['hasCoordinates'] = False

            # in case set attachment data
            temp_url = None
            if activity['hasAttachment']:
                # check different actor
                if 'actor' in item['object'] and 'id' in item['object']['actor']:
                    activity['actorId'] = item['object']['actor']['id']

                # scroll attachments
                for attachment in item['object']['attachments']:
                    # check attachment type
                    if 'objectType' in attachment and attachment['objectType'] == 'article':
                        # article

                        activity['attachmentTitle'] = attachment.get('displayName', '')
                        activity['attachmentContent'] = attachment.get('content', '')
                        activity['attachmentUrl'] = attachment.get('url', '')

                    elif 'objectType' in attachment and attachment['objectType'] == 'photo':
                        # photo

                        temp_url = attachment['url']
                        if 'url' in attachment['image']:
                            activity['imageUrl'] = attachment['image']['url']
                        if 'width' in attachment['image']:
                            activity['imageWidth'] = attachment['image']['width']
                        if 'height' in attachment['image']:
                            activity['imageHeight'] = attachment['image']['height']

                # check activity URL
                if 'attachmentUrl' not in activity and temp_url is not None:
                    activity['attachmentUrl'] = temp_url

            if name is None and item['actor']['id'] == user_id:
                name = item['actor']['displayName']

            process_activity_data(activity)
            activities.append(activity)

        return {'name': name or 'unknown', 'activities': activities, 'user_id': user_id, 'photo_url': feed.photo_url}

    class UserIdNotFoundException(Exception):
        pass

    class FeedNotFoundException(Exception):
        pass
