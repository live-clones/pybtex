import importlib
import nose.tools

import pybtex.database.input.bibtex
import pybtex.plugin
import pybtex.plugin.loader
import pybtex.style.formatting.plain

def test_plugin_loader():
    """Check that all enumerated plugins can be imported."""
    for group in pybtex.plugin.loader.PLUGIN_GROUPS:
        for name in pybtex.plugin.enumerate_plugin_names(group):
            pybtex.plugin.find_plugin(group, name)

def test_builtin_plugin_module_class_datas():
    for module_name, class_name, plugin_data in pybtex.plugin.loader.builtin_plugin_module_class_datas():
        plugin = getattr(importlib.import_module(module_name), class_name)
        nose.tools.assert_is(plugin, pybtex.plugin.find_plugin(
            plugin_data.plugin_group, plugin_data.plugin_name))
        nose.tools.assert_equal(plugin_data.plugin_name, plugin.name)
        nose.tools.assert_equal(plugin_data.suffixes, plugin.suffixes)
        nose.tools.assert_equal(plugin_data.aliases, plugin.aliases)

class TestPlugin1(pybtex.plugin.Plugin):
    name = 'yippikayee'

class TestPlugin2(pybtex.plugin.Plugin):
    name = 'plain'

class TestPlugin3(pybtex.plugin.Plugin):
    name = 'yippikayeetoo'
    aliases = ('plain',)

def test_register_plugin_1():
    pybtex.plugin.register_plugin('pybtex.style.formatting', TestPlugin1)
    nose.tools.assert_is(
        TestPlugin1, pybtex.plugin.find_plugin(
            'pybtex.style.formatting', 'yippikayee'))

def test_register_plugin_2():
    pybtex.plugin.register_plugin('pybtex.style.formatting', TestPlugin2)
    plugin = pybtex.plugin.find_plugin('pybtex.style.formatting', 'plain')
    nose.tools.assert_is_not(plugin, TestPlugin2)
    nose.tools.assert_is(plugin, pybtex.style.formatting.plain.Style)

def test_register_plugin_3():
    pybtex.plugin.register_plugin('pybtex.style.formatting', TestPlugin3)
    plugin = pybtex.plugin.find_plugin('pybtex.style.formatting', 'plain')
    nose.tools.assert_is_not(plugin, TestPlugin3)
    nose.tools.assert_is(plugin, pybtex.style.formatting.plain.Style)

def test_bad_plugin():
    nose.tools.assert_raises(
        pybtex.plugin.loader.PluginGroupNotFound,
        lambda: pybtex.plugin.find_plugin("pybtex.invalid.group", "__oops"))
    nose.tools.assert_raises(
        pybtex.plugin.loader.PluginNotFound,
        lambda: pybtex.plugin.find_plugin("pybtex.style.formatting", "__oops"))
    nose.tools.assert_raises(
        pybtex.plugin.loader.PluginNotFound,
        lambda: pybtex.plugin.find_plugin("pybtex.style.formatting",
                                          filename="oh.__oops"))

def test_plugin_suffix():
    plugin = pybtex.plugin.find_plugin(
        "pybtex.database.input", filename="test.bib")
    nose.tools.assert_is(plugin, pybtex.database.input.bibtex.Parser)

def test_entry_point():
    # create artificial entry point and re-register just for testing;
    # in practice you would not do this in real production code
    import pkg_resources
    dist = pkg_resources.get_distribution('pybtex')
    ep_map = pkg_resources.get_entry_map(dist)
    assert "pybtex.database.input" not in ep_map
    ep_map["pybtex.database.input"] = {
        "woohahaha": pkg_resources.EntryPoint(
            "woohahaha", "pybtex.database.input.bibtex",
            attrs=("Parser",), dist=dist)}
    assert "pybtex.database.input.suffixes" not in ep_map
    ep_map["pybtex.database.input.suffixes"] = {
        ".woo": pkg_resources.EntryPoint(
            ".woo", "pybtex.database.input.bibtex",
            attrs=("Parser",), dist=dist)}
    pybtex.plugin.plugin_loader._register_entry_point_plugins()
    p1 = pybtex.plugin.find_plugin("pybtex.database.input", "woohahaha")
    nose.tools.assert_is(p1, pybtex.database.input.bibtex.Parser)
    p2 = pybtex.plugin.find_plugin("pybtex.database.input", filename="t.woo")
    nose.tools.assert_is(p2, pybtex.database.input.bibtex.Parser)
