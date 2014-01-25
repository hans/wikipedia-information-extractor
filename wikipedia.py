"""Various helper functions that work with Wikipedia content"""

import re
import urllib

WIKI_LINK_HEAD = re.compile(r'^/?wiki/')

def get_wikilinks(doc):
    """Extract all wikilinks from an `lxml.etree` document. Returns a
    list of tuples of the form `(page_name, link_text)`."""

    links = doc.xpath('//div[@id="mw-content-text"]'
                      '//a[starts-with(@href, "/wiki/")]')

    for link in links:
        if not link.text:
            continue

        page_name = WIKI_LINK_HEAD.sub('', link.attrib['href'])
        page_name = link_to_page_name(page_name)

        yield page_name, link.text


def link_to_page_name(href):
    """Convert a Wikipedia page name as it exists in an HTML link into
    human-readable form."""

    # TODO: Probably need more than this
    return urllib.unquote(href.replace('_', ' '))
