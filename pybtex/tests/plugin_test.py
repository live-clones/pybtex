import importlib
import nose.tools

import pybtex.plugin
import pybtex.plugin.loader


def test_plugin_loader():
    """Check that all enumerated plugins can be imported."""
    for group in pybtex.plugin.PLUGIN_GROUPS:
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
