import nose.tools

import pybtex.database.input.bibtex
import pybtex.plugin
import pybtex.style.formatting.plain

def test_plugin_loader():
    """Check that all enumerated plugins can be imported."""
    for group in pybtex.plugin._DEFAULT_PLUGINS:
        for name in pybtex.plugin.enumerate_plugin_names(group):
            pybtex.plugin.find_plugin(group, name)

class TestPlugin1(pybtex.plugin.Plugin):
    pass

class TestPlugin2(pybtex.plugin.Plugin):
    pass

class TestPlugin3(pybtex.plugin.Plugin):
    pass

def test_register_plugin_1():
    pybtex.plugin.register_plugin(
        'pybtex.style.formatting', 'yippikayee', TestPlugin1)
    nose.tools.assert_is(
        TestPlugin1, pybtex.plugin.find_plugin(
            'pybtex.style.formatting', 'yippikayee'))

def test_register_plugin_2():
    pybtex.plugin.register_plugin(
        'pybtex.style.formatting', 'plain', TestPlugin2)
    plugin = pybtex.plugin.find_plugin('pybtex.style.formatting', 'plain')
    nose.tools.assert_is_not(plugin, TestPlugin2)
    nose.tools.assert_is(plugin, pybtex.style.formatting.plain.Style)

def test_register_plugin_3():
    pybtex.plugin.register_plugin(
        'pybtex.style.formatting.suffixes', '.woo', TestPlugin3)
    plugin = pybtex.plugin.find_plugin(
        'pybtex.style.formatting', filename='test.woo')
    nose.tools.assert_is(plugin, TestPlugin3)

def test_bad_find_plugin():
    nose.tools.assert_raises(
        pybtex.plugin.PluginGroupNotFound,
        lambda: pybtex.plugin.find_plugin("pybtex.invalid.group", "__oops"))
    nose.tools.assert_raises(
        pybtex.plugin.PluginNotFound,
        lambda: pybtex.plugin.find_plugin("pybtex.style.formatting", "__oops"))
    nose.tools.assert_raises(
        pybtex.plugin.PluginNotFound,
        lambda: pybtex.plugin.find_plugin("pybtex.style.formatting",
                                          filename="oh.__oops"))

def test_bad_register_plugin():
    nose.tools.assert_raises(
        pybtex.plugin.PluginGroupNotFound,
        lambda: pybtex.plugin.register_plugin(
            "pybtex.invalid.group", "__oops", TestPlugin1))
    nose.tools.assert_raises(
        pybtex.plugin.PluginGroupNotFound,
        lambda: pybtex.plugin.register_plugin(
            "pybtex.invalid.group.suffixes", ".__oops", TestPlugin1))
    # suffixes must start with a dot
    nose.tools.assert_raises(
        ValueError,
        lambda: pybtex.plugin.register_plugin(
            "pybtex.style.formatting.suffixes", "notasuffix", TestPlugin1))

def test_plugin_suffix():
    plugin = pybtex.plugin.find_plugin(
        "pybtex.database.input", filename="test.bib")
    nose.tools.assert_is(plugin, pybtex.database.input.bibtex.Parser)