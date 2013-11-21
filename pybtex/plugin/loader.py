# Copyright (c) 2007, 2008, 2009, 2010, 2011, 2012  Andrey Golovizin
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import importlib
import os.path  # splitext
from itertools import chain

from pybtex.exceptions import PybtexError


class PluginGroupNotFound(PybtexError):
    def __init__(self, group_name):
        message = u'plugin group {group_name} not found'.format(
            group_name=group_name,
        )
        super(PluginGroupNotFound, self).__init__(message)


class PluginNotFound(PybtexError):
    def __init__(self, plugin_group, name=None, filename=None):
        assert plugin_group
        if name:
            message = u'plugin {plugin_group}.{name} not found'.format(
                plugin_group=plugin_group,
                name=name,
            )
        elif filename:
            message = u'cannot determine file type for {filename}'.format(
                plugin_group=plugin_group,
                filename=filename,
            )
        else:
            message = u'plugin group {plugin_group} has no default'.format(
                plugin_group=plugin_group,
            )

        super(PluginNotFound, self).__init__(message)


class PluginLoader(object):
    """Plugin loader base class."""

    #: list of all pybtex plugin groups
    PLUGIN_GROUPS = (
        "pybtex.database.input",
        "pybtex.database.output",
        "pybtex.backends",
        "pybtex.style.labels",
        "pybtex.style.names",
        "pybtex.style.sorting",
        "pybtex.style.formatting",
        )

    def __init__(self):
        # data structure
        # do not manipulate directly: use the register_xxx methods
        self._plugin_registry = {
            plugin_group: {
                #: map plugin names to plugin classes
                "plugins": {},
                #: map file suffixes to plugin classes
                "suffixes": {},
                #: default plugin class
                "default_plugin": None,
                }
            for plugin_group in self.PLUGIN_GROUPS
            }
        self._register_builtin_plugins()
        self._register_entry_point_plugins()

    # implementation note: always use _get_group_info
    # do not use self._plugin_registry[plugin_group]
    # this ensures consistent exceptions are raised
    def _get_group_info(self, plugin_group):
        """Get plugin group info. Raises PluginGroupNotFound if
        *plugin_group* does not exist.
        """
        try:
            plugin_group_info = self._plugin_registry[plugin_group]
        except KeyError:
            raise PluginGroupNotFound(plugin_group)
        return plugin_group_info

    def register_plugin(self, plugin_group, klass):
        plugin_group_info = self._get_group_info(plugin_group)
        if klass.name in plugin_group_info["plugins"]:
            # XXX could raise an exception
            print("Warning: plugin {name} already registered in group {plugin_group}".format(name=klass.name, plugin_group=plugin_group))
            return
        plugin_group_info["plugins"][klass.name] = klass
        if not plugin_group_info["default_plugin"]:
            plugin_group_info["default_plugin"] = klass
        for suffix in klass.suffixes:
            plugin_group_info["suffixes"][suffix] = klass
        for alias in klass.aliases:
            plugin_group_info["plugins"][alias] = klass

    def find_plugin(self, plugin_group, name=None, filename=None):
        """Find a :class:`Plugin` class within *plugin_group* which
        matches *name*, or *filename* if *name* is not specified, or
        the default plugin if neither *name* nor *filename* is
        specified.

        If *name* is specified, return the :class:`Plugin` class
        registered under *name*. If *filename* is specified, look at
        its suffix (i.e. extension) and return the :class:`Plugin`
        class registered for this suffix.
        """
        plugin_group_info = self._get_group_info(plugin_group)
        if name:
            if name in plugin_group_info['plugins']:
                return plugin_group_info['plugins'][name]
            else:
                raise PluginNotFound(plugin_group, name=name)
        elif filename:
            suffix = os.path.splitext(filename)[1]
            if suffix in plugin_group_info['suffixes']:
                return find_plugin(
                    plugin_group, plugin_group_info['suffixes'][suffix])
            else:
                raise PluginNotFound(plugin_group, filename=filename)
        else:
            plugin = plugin_group_info['default_plugin']
            if plugin:
                return plugin
            else:
                raise PluginNotFound(plugin_group)

    def enumerate_plugin_names(self, plugin_group):
        """Enumerate all plugin names for the given *plugin_group*."""
        return self._get_group_info(plugin_group)["plugins"].iterkeys()

    def _register_builtin_plugins(self):
        BUILTIN_PLUGINS = (
            ("pybtex.database.input", "Parser"),
            ("pybtex.database.output", "Writer"),
            ("pybtex.backends", "Backend"),
            ("pybtex.style.labels", "LabelStyle"),
            ("pybtex.style.names", "NameStyle"),
            ("pybtex.style.sorting", "SortingStyle"),
            ("pybtex.style.formatting", "Style"),
            )
        assert set(grp for grp, kls in BUILTIN_PLUGINS) == set(self.PLUGIN_GROUPS)
        for plugin_group, class_name in BUILTIN_PLUGINS:
            for plugin in self._get_builtin_plugins(plugin_group, class_name):
                self.register_plugin(plugin_group, plugin)

    def _get_builtin_plugins(self, plugin_group, class_name):
        base_module = importlib.import_module(plugin_group)
        base_plugin = getattr(base_module, "Base" + class_name)
        for plugin_name in base_plugin.builtin_plugins:
            plugin_module = importlib.import_module(
                plugin_group + "." + plugin_name)
            klass = getattr(plugin_module, class_name)
            assert klass.name == plugin_name
            yield klass

    def _register_entry_point_plugins(self):
        try:
            import pkg_resources
        except ImportError:
            return
        for plugin_group in self.PLUGIN_GROUPS:
            for entry_point in pkg_resources.iter_entry_points(plugin_group):
                klass = entry_point.load()
                self.register_plugin(plugin_group, klass)

plugin_loader = PluginLoader()
