from six.moves import map

from collective.solr import mangler
from collective.solr.mangler import makeSimpleExpressions
from collective.solr.queryparser import quote
from collective.solr.utils import getConfig
from collective.solr.utils import isSimpleSearch
from collective.solr.utils import removeSpecialCharactersAndOperators
from collective.solr.utils import splitSimpleSearch
from graffiti.search import logger


# noinspection DuplicatedCode
def patched_mangleSearchableText(value, config, force_complex_search=False):
    config = config or getConfig()
    pattern = getattr(config, "search_pattern", u"")
    force_simple_search = getattr(config, "force_simple_search", False)
    allow_complex_search = getattr(config, "allow_complex_search", False)
    levenstein_distance = getattr(config, "levenshtein_distance", 0)
    prefix_wildcard = getattr(config, "prefix_wildcard", False)
    value_parts = []
    base_value_parts = []

    stripped = value.strip()
    force_complex_search_prefix = False
    if stripped.startswith("solr:"):
        stripped = stripped.replace("solr:", "", 1).strip()
        force_complex_search_prefix = True

    if not force_simple_search and not isSimpleSearch(value):
        return value

    if allow_complex_search and (force_complex_search_prefix or force_complex_search):
        # FIXME: fold in catalog solr_complex_search parameter check
        return stripped

    # INTERAKTIV - START
    raw_value = value
    # INTERAKTIV - END

    if force_simple_search:
        value = removeSpecialCharactersAndOperators(value)

    for term in splitSimpleSearch(value):
        (term_value, term_base_value) = makeSimpleExpressions(term, levenstein_distance)
        value_parts.append(term_value)
        base_value_parts.append(term_base_value)

    base_value = " ".join(base_value_parts)
    value = " ".join(value_parts)
    if pattern:
        # INTERAKTIV - START
        value = pattern.format(
            value=quote(value, prefix_wildcard=prefix_wildcard),
            base_value=base_value,
            raw_value=raw_value
        )
        # INTERAKTIV - END
        return set([value])  # add literal query parameter
    if pattern:
        pattern = pattern.encode("utf-8")
    return value


def apply_patch():
    logger.info("Applying patch")
    mangler.mangleSearchableText = patched_mangleSearchableText
