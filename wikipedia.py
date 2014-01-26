"""Various helper functions that work with Wikipedia content"""

import json
import re
import urllib

from google.appengine.api import urlfetch
from lxml import etree

from util import STOPWORDS


PARSER = etree.XMLParser(encoding='utf-8')


def _fetch(url):
    """Fetch the contents of a URL as a string."""

    content = None

    try:
        result = urlfetch.fetch(url, deadline=20)
    except AssertionError: # urlfetch not supported
        content = urllib.urlopen(url).read()
    else:
        if result.status_code != 200:
            return None
        content = result.content

    return content


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
    'inspired by',
    'derived from',
    'birthplace of',
    'led to',
]
TRIGGER_CONTEXT_PATTERNS = [re.compile(r, re.I) for r in TRIGGER_CONTEXT_PATTERNS]

# Patterns which, when near a link, hint that the link is unimportant /
# especially irrelevant
UNLIKELY_CONTEXT_PATTERNS = [
    'for example',
    'such as'
]
UNLIKELY_CONTEXT_PATTERNS = [re.compile(r, re.I) for r in UNLIKELY_CONTEXT_PATTERNS]


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

    # Add score based on number of backlinks
    backlinks = get_page_backlinks(wikilink.page_name[1])
    score += 1/400.0 * backlinks

    # Penalize list pages
    if wikilink.page_name[1].startswith('List of'):
        score -= 0.5

    # Sentences which share words with the page name should be weighted
    # higher
    #
    # TODO: Better tokenization?
    # shared_words = (set(wikilink.page_name[1].split())
    #                 & (set(wikilink.context[0].split())
    #                    | set(wikilink.context[1].split()))) - STOPWORDS
    # score += len(shared_words) / 2.0

    start_context, end_context = wikilink.context

    for pattern in TRIGGER_CONTEXT_PATTERNS:
        if pattern.search(start_context) or pattern.search(end_context):
            score *= 1.25

    for pattern in UNLIKELY_CONTEXT_PATTERNS:
        if pattern.search(start_context) or pattern.search(end_context):
            score /= 1.25

    return score


def fetch_page((namespace, page_name, section_name)):
    """Fetch the Wikipedia page with the given namespace, title and
    section name. (`namespace` and `section` may be `None.`) Returns an
    `lxml` document or `None` if the page could not be found."""

    url = page_name_to_link((namespace, page_name, section_name))
    return etree.fromstring(_fetch(url), parser=PARSER)


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
            links.extend(el.xpath('.//a[starts-with(@href, "/wiki/")]'))

        for link in links:
            if not link.text:
                continue

            page_name = WIKI_LINK_HEAD.sub('', link.attrib['href'])
            page_name = link_to_page_name(page_name)

            yield Wikilink(section_name, page_name, link.text,
                           get_context(link))


WIKI_LINK_HEAD = re.compile(r'^/?wiki/')
WIKI_LINK = re.compile(r'^(?:(.+?):)?(.+?)(?:\#(.+))?$')

def link_to_page_name(href):
    """Convert a Wikipedia page name as it exists in an HTML link into
    human-readable form. Returns a tuple `(namespace, page_name,
    section_name)`, where `namespace` and `section_name` may be `None`."""

    cleaned = urllib.unquote(href.replace('_', ' '))
    return WIKI_LINK.match(cleaned).groups()


def page_name_to_link((namespace, page_name, section_name)):
    """Convert a page-name tuple of the form `(namespace, page_name,
    section_name`) into a Wikipedia link."""

    url = 'http://en.wikipedia.org/wiki/'
    post = ''

    if namespace is not None:
        post += namespace + ':'

    post += page_name.replace(' ', '_')

    if section_name is not None:
        post += '#' + section_name.replace(' ', '#')

    return url + urllib.quote(post)


WIKIPEDIA_SUGGESTION_URL = ("https://en.wikipedia.org/w/api.php?action=query"
                            "&list=search&format=json&srprop=snippet"
                            "&srinfo=suggestion&srlimit=1&srsearch=%s")

def get_page_for_query(query):
    """Get the name of the best-matching page for a search query.
    (Searches in the main namespace only.)"""

    url = WIKIPEDIA_SUGGESTION_URL % urllib.quote(query)
    content = _fetch(url)

    suggestions = json.loads(content)['query']['search']
    if not suggestions:
        return None

    return suggestions[0]['title']


WIKIPEDIA_BACKLINK_URL = ("https://en.wikipedia.org/w/api.php?action=query"
                          "&list=backlinks&format=json&bllimit=500"
                          "&blnamespace=0&blfilterredir=nonredirects"
                          "&bltitle=%s")

def get_page_backlinks(title):
    """Find the number of pages (up to 500) which link to a page with a
    given title. If the number of pages of this type is over 500, the
    function returns 501."""

    url = WIKIPEDIA_BACKLINK_URL % urllib.quote(title)
    data = json.loads(_fetch(url))
    count = len(data['query']['backlinks'])

    if 'query-continue' in data:
        return 501
    return count
