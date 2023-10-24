import bleach
import logging


def sanitize_html(html):
    # Allow only a limited set of tags and attributes
    allowed_tags = ['a', 'b', 'i', 'em', 'strong']
    allowed_attributes = {'a': ['href']}
    return bleach.clean(html, tags=allowed_tags, attributes=allowed_attributes)


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
