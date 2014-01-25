"""Various helper functions that work with Wikipedia content"""

import re
import urllib


SECTION_WEIGHTS = {
    'Name': 0.4,
    'Etymology': 0.4,
    'See also': 0.9,
    'References': 0,
}


def score_wikilink((section_name, page_name, link_text)):
    """Return a score for a wikilink `link` (a tuple of the form
    `(section_name, page_name, link_text)`)."""

    # TODO smarter weighting

    section_weight = SECTION_WEIGHTS.get(section_name, 1)
    return section_weight


def get_relevant_pages(doc):
    """Get a list of page names which are relevant to an `lxml.etree`
    document for a Wikipedia page."""

    scored = {link: score_wikilink(link) for link in get_wikilinks(doc)}
    return sorted(scored.iteritems(), reverse=True, key=lambda (l, s): s)[:10]


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


def get_wikilinks(doc, skip_sections=('References', 'Notes')):
    """Extract all wikilinks from an `lxml.etree` document. Returns a
    list of tuples of the form `(section_index, page_name, link_text)`.

    Skips reading links from section names which match `skip_sections`."""

    for section_name, section in get_sections(doc):
        if section_name in skip_sections:
            continue

        links = []
        for el in section:
            links.extend(el.xpath('//a[starts-with(@href, "/wiki/")]'))

        for link in links:
            if not link.text:
                continue

            page_name = WIKI_LINK_HEAD.sub('', link.attrib['href'])
            page_name = link_to_page_name(page_name)

            yield section_name, page_name, link.text


WIKI_LINK_HEAD = re.compile(r'^/?wiki/')
WIKI_LINK = re.compile(r'^(?:(.+?):)?(.+?)(?:\#(.+))?$')

def link_to_page_name(href):
    """Convert a Wikipedia page name as it exists in an HTML link into
    human-readable form. Returns a tuple `(namespace, page_name,
    section_name)`, where `namespace` and `section_name` may be `None`."""

    cleaned = urllib.unquote(href.replace('_', ' '))
    return WIKI_LINK.match(cleaned).groups()
