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

from feedgen.ext.base import BaseEntryExtension
from lxml import etree


class MediaEntryExtension(BaseEntryExtension):
    def __init__(self):
        self.__thumbnail_url = None
        self.__thumbnail_width = None
        self.__thumbnail_height = None

    def extend_rss(self, entry):
        MEDIA_NS = 'http://search.yahoo.com/mrss/'

        if self.__thumbnail_url:
            thumbnail = etree.SubElement(entry, '{%s}thumbnail' % MEDIA_NS)
            thumbnail.attrib['url'] = self.__thumbnail_url

            if self.__thumbnail_width and self.__thumbnail_height:
                thumbnail.attrib['width'] = self.__thumbnail_width
                thumbnail.attrib['height'] = self.__thumbnail_height

    def media_thumbnail_url(self, url=None):
        if url is not None:
            self.__thumbnail_url = url

        return self.__thumbnail_url

    def media_thumbnail_width(self, width=None):
        if width is not None:
            self.__thumbnail_width = width

        return self.__thumbnail_width

    def media_thumbnail_height(self, height=None):
        if height is not None:
            self.__thumbnail_height = height

        return self.__thumbnail_height
