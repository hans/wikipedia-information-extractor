"""Various helper functions that work with Wikipedia content"""

import re
import urllib

from lxml import etree


SECTION_SCORES = {
    None: 1.4,
    'Name': 0.4,
    'Etymology': 0.4,
    'See also': 0.9,
    'References': 0,
}


# Patterns which, when near a link, hint that the link is important /
# especially relevant
TRIGGER_CONTEXT_PATTERNS = [
    'became',
    'was an',
    'is an',
    'author of',
    'main article',
]
TRIGGER_CONTEXT_PATTERNS = [re.compile(r, re.I) for r in TRIGGER_CONTEXT_PATTERNS]


class Wikilink(object):
    def __init__(self, section_name, page_name, link_text, context):
        self.section_name = section_name
        self.page_name = page_name
        self.link_text = link_text
        self.context = context

    def __str__(self):
        return '<Wikilink "%s">' % self.link_text

    def __repr__(self):
        return 'Wikilink(%r, %r, %r, %r)' % (self.section_name, self.page_name,
                                             self.link_text, self.context)


def score_wikilink(wikilink):
    """Return a score for a Wikilink `link`."""

    score = SECTION_SCORES.get(wikilink.section_name, 1)

    start_context, end_context = wikilink.context
    for pattern in TRIGGER_CONTEXT_PATTERNS:
        if pattern.search(start_context) or pattern.search(end_context):
            score *= 1.25

    return score


def get_relevant_pages(doc):
    """Get a list of page names which are relevant to an `lxml.etree`
    document for a Wikipedia page.

    Returns a list of tuples of the form `(namespace, page_name,
    anchor)`, where `namespace` and `anchor` may each be `None`."""

    scored = {link: score_wikilink(link) for link in get_wikilinks(doc)}
    results = sorted(scored.iteritems(), reverse=True,
                     key=lambda (l, s): s)[:10]
    return [link.page_name for link, _ in results]


def get_sections(doc):
    """Split a Wikipedia `lxml.etree` document into a list of section
    fragments. Yields tuples of the form `(section_name,
    section_lxml_fragment)`."""

    content = doc.xpath('//div[@id="mw-content-text"]')[0]
    separators = [0] + [i for i, el in enumerate(content) if el.tag == 'h2']

    for sep1, sep2 in zip(separators, separators[1:]):
        name_match = content[sep1].xpath('span[@class="mw-headline"]/text()')
        name = name_match and name_match[0] or None
        yield name, content[sep1 + 1:sep2]


def get_context(link_el, max_context_size=10):
    """Determine the token context for a given link element."""

    parent_content = etree.tostring(link_el.getparent(), encoding='utf-8',
                                    method='text')

    context = re.search(r'((?:[\w,:]+\s){0,10})%s[,:\s]+((?:[\w,:]+\s){0,10})'
                        % link_el.text, parent_content)

    if not context:
        return ('', '')

    return context.groups()


def get_wikilinks(doc, skip_sections=('References', 'Notes')):
    """Extract all wikilinks from an `lxml.etree` document. Returns a
    list of tuples of the form `(section_index, page_name, link_text)`.

    Skips reading links from section names which match `skip_sections`."""

    for section_name, section in get_sections(doc):
        if section_name in skip_sections:
            continue

        links = []
        for el in section:
            links.extend(el.xpath('a[starts-with(@href, "/wiki/")]'))

        for link in links:
            if not link.text:
                continue

            page_name = WIKI_LINK_HEAD.sub('', link.attrib['href'])
            page_name = link_to_page_name(page_name)

            yield Wikilink(section_name, page_name, link.text,
                           get_context(link))
            break


WIKI_LINK_HEAD = re.compile(r'^/?wiki/')
WIKI_LINK = re.compile(r'^(?:(.+?):)?(.+?)(?:\#(.+))?$')

def link_to_page_name(href):
    """Convert a Wikipedia page name as it exists in an HTML link into
    human-readable form. Returns a tuple `(namespace, page_name,
    section_name)`, where `namespace` and `section_name` may be `None`."""

    cleaned = urllib.unquote(href.replace('_', ' '))
    return WIKI_LINK.match(cleaned).groups()
