import pytest
from pybtex.style.template import href, words


def test_old_href_syntax():
    with pytest.warns(
        DeprecationWarning,
        match=r'href \[url, text\] is deprecated since 0\.24'
    ):
        result = href ['www.test.org', 'click here'].format().render_as('html')
    assert result == '<a href="www.test.org">click here</a>'

    with pytest.warns(
        DeprecationWarning,
        match=r'href \[url, text\] is deprecated since 0\.24'
    ):
        result = href [words ['www.test2.org'], words ['click', 'here!']].format().render_as('html')
    assert result == '<a href="www.test2.org">click here!</a>'


