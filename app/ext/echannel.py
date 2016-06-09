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

from feed.rss import *

s_href = 'href'
s_rel = 'rel'


class EChannel(Channel):
    def __init__(self):
        NestElement.__init__(self, "channel")

        self.title = Title("title of feed goes here")
        self.link = Link("URL link to feed goes here")
        self.description = Description("description of feed goes here")
        self.language = Language()
        self.copyright = Copyright()
        self.managing_editor = ManagingEditor()
        self.web_master = WebMaster()
        self.pub_date = PubDate()
        self.last_build_date = LastBuildDate()
        self.categories = Collection(Category)
        self.generator = Generator()
        self.docs = Docs()
        self.cloud = Cloud()
        self.ttl = TTL()
        self.image = Image()
        self.rating = Rating()
        self.text_input = TextInput()
        self.skip_hours = SkipHours()
        self.skip_days = SkipDays()
        self.atom_link = AtomLink()

        self.items = Collection(Item)


class AtomLink(TextElement):
    def __init__(self, href='', rel='self'):
        TextElement.__init__(self, 'atom:link')
        self.attrs[s_href] = href
        self.attrs[s_rel] = rel


def new_xmldoc_echannel():
    """
    Creates a new XMLDoc() with a EChannel() in it.  Returns both as a tuple.

    Return a tuple: (rss, echannel)
    """
    xmldoc = XMLDoc()
    rss = RSS()
    xmldoc.root_element = rss

    channel = EChannel()
    channel.generator = module_banner
    rss.channel = channel

    return xmldoc, channel
