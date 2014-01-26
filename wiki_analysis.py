"""Special routines powered by NLP analysis on Wikipedia pages / using
Wikipedia pages."""

import re

from lxml import etree

import wikipedia


PARENTHETICAL_EXPRESSION = re.compile(r'(?<=\s)\([^)]+?\)\s*(\.?)')

def get_definition(term, document=None):
    """Get a definition for a term. Caller can optionally provide the
    `lxml` document in which the term was first found (and thus where a
    definition may also be found)."""

    # First stab: try to fetch a relevant article
    page_name = wikipedia.get_page_for_query(term)
    document = wikipedia.fetch_page((None, page_name, None))

    if document is None:
        # TODO: Other extraction method
        return

    content_el = document.xpath('//div[@id="mw-content-text"]/p[1]')[0]

    text_content = etree.tostring(content_el, method='text',
                                  encoding='utf-8')
    text_content = PARENTHETICAL_EXPRESSION.sub(r'\1', text_content)

    # Grab first sentence.
    # TODO: Better sentence segmentation
    sentence = text_content.split('.')[0]

    return sentence.strip() + '.'
