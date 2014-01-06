# IMPORTANT: to register new builtin modules, update builtin_plugin_datas



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


import collections
import importlib  # import_module (to load builtin plugins)
import os.path  # splitext

from pybtex.exceptions import PybtexError


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


#: Registration data of a plugin class.
PluginData = collections.namedtuple(
    "PluginData", "plugin_group plugin_name suffixes aliases")

def builtin_plugin_module_class_datas():
    """Yield triples (module_name, class_name, plugin_data)
    for all builtin modules.
    """

    # the first plugin returned within a plugin group is the default plugin

    def module_class_data(class_name, plugin_group, plugin_name,
                          suffixes=(), aliases=()):
        """Module name, class name, and plugin data."""
        return (
            ".".join((plugin_group, plugin_name)), class_name,
            PluginData(plugin_group, plugin_name, suffixes, aliases)
            )

    # data input and output
    for mode, class_name in (("input", "Parser"), ("output", "Writer")):
        for plugin_name, suffixes, aliases in (
            ("bibtex", (".bib",), ()),
            ("bibtexml", (".xml", ".bibtexml"), ()),
            ("bibyaml", (".yaml", ".bibyaml"), ("yaml",)),
            ):
            yield module_class_data(
                class_name=class_name,
                plugin_group="pybtex.database.%s" % mode,
                plugin_name=plugin_name,
                suffixes=suffixes,
                aliases=aliases,
                )
    # formatting backends
    for plugin_name, suffixes, aliases in (
        ("latex", (".bbl", ".tex", ".latex"), ()),
        ("html", (".html",), ()),
        ("plaintext", (".txt",), ("text",)),
        ):
        yield module_class_data(
            class_name="Backend",
            plugin_group="pybtex.backends", plugin_name=plugin_name,
            suffixes=suffixes, aliases=aliases)
    # styles
    for plugin_name in ('number', 'alpha'):
        yield module_class_data(
            class_name="LabelStyle",
            plugin_group="pybtex.style.labels", plugin_name=plugin_name)
    for plugin_name, aliases in (
        ('plain', ()),
        ('lastfirst', ('last_first',))):
        yield module_class_data(
            class_name="NameStyle",
            plugin_group="pybtex.style.names", plugin_name=plugin_name,
            aliases=aliases)
    for plugin_name in ('none', 'author_year_title'):
        yield module_class_data(
            class_name="SortingStyle",
            plugin_group="pybtex.style.sorting", plugin_name=plugin_name)
    for plugin_name in ("unsrt", "plain", "alpha", "unsrtalpha"):
        yield module_class_data(
            class_name="Style",
            plugin_group="pybtex.style.formatting", plugin_name=plugin_name)

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


class LazyPlugin(object):
    """A plugin class wrapper that creates the plugin class only when
    needed. We use this so we can register many plugins whilst
    avoiding the overhead of importing all modules.
    """

    def __init__(self):
        self._klass = None

    def load(self):
        """Return plugin class. Overload this method."""
        raise NotImplementedError

    def get_plugin(self, *args, **kwargs):
        """Return plugin class, loading it if need be.
        You should not need to overload this method.
        """
        if self._klass is None:
            self._klass = self.load()
        return self._klass


class LazyModulePlugin(LazyPlugin):
    def __init__(self, module_name, class_name):
        LazyPlugin.__init__(self)
        self.module_name = module_name
        self.class_name = class_name

    def load(self):
        return getattr(
            importlib.import_module(self.module_name), self.class_name)


class LazyEntryPointPlugin(LazyPlugin):
    def __init__(self, entry_point):
        LazyPlugin.__init__(self)
        self.entry_point = entry_point

    def load(self):
        return self.entry_point.load()


class LazyClassPlugin(LazyPlugin):
    """Not really a lazy plugin, but useful for registering classes
    directly.
    """

    def __init__(self, plugin_class):
        self._klass = plugin_class


class PluginLoader(object):
    """Plugin loader base class."""

    def __init__(self):
        # data structure
        # do not manipulate directly: use the register_plugin method
        self._plugin_registry = {
            plugin_group: {
                #: map plugin names to (lazy) plugin classes
                "plugins": {},
                #: map file suffixes to (lazy) plugin classes
                "suffixes": {},
                #: default (lazy) plugin class
                "default_plugin": None,
                }
            for plugin_group in PLUGIN_GROUPS
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

    def register_plugin(self, plugin_group, plugin_class):
        self.register_lazy_plugin(
            LazyClassPlugin(plugin_class),
            PluginData(
                plugin_group=plugin_group,
                plugin_name=plugin_class.name,
                suffixes=plugin_class.suffixes,
                aliases=plugin_class.aliases,
                ))

    def register_lazy_plugin(self, lazy_plugin, plugin_data):
        plugin_group_info = self._get_group_info(plugin_data.plugin_group)
        if plugin_data.plugin_name in plugin_group_info["plugins"]:
            # XXX could raise an exception
            print("Warning: plugin {name} already registered in group {plugin_group}"
                  .format(name=plugin_data.plugin_name,
                          plugin_group=plugin_data.plugin_group))
            return
        plugin_group_info["plugins"][plugin_data.plugin_name] = lazy_plugin
        if not plugin_group_info["default_plugin"]:
            plugin_group_info["default_plugin"] = lazy_plugin
        for suffix in plugin_data.suffixes:
            plugin_group_info["suffixes"][suffix] = lazy_plugin
        for alias in plugin_data.aliases:
            if alias in plugin_group_info["plugins"]:
                print("Warning: plugin {name} already registered in group {plugin_group}"
                      .format(name=alias, plugin_group=plugin_group))
            else:
                plugin_group_info["plugins"][alias] = lazy_plugin

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
                return plugin_group_info['plugins'][name].get_plugin()
            else:
                raise PluginNotFound(plugin_group, name=name)
        elif filename:
            suffix = os.path.splitext(filename)[1]
            if suffix in plugin_group_info['suffixes']:
                return plugin_group_info['suffixes'][suffix].get_plugin()
            else:
                raise PluginNotFound(plugin_group, filename=filename)
        else:
            plugin = plugin_group_info['default_plugin']
            if plugin is not None:
                return plugin.get_plugin()
            else:
                raise PluginNotFound(plugin_group)

    def enumerate_plugin_names(self, plugin_group):
        """Enumerate all plugin names for the given *plugin_group*."""
        return self._get_group_info(plugin_group)["plugins"].iterkeys()

    def _register_builtin_plugins(self):
        for module_name, class_name, plugin_data in builtin_plugin_module_class_datas():
            assert plugin_data.plugin_group in PLUGIN_GROUPS
            lazy_plugin = LazyModulePlugin(module_name, class_name)
            self.register_lazy_plugin(lazy_plugin, plugin_data)

    def _register_entry_point_plugins(self):
        try:
            import pkg_resources
        except ImportError:
            return
        for plugin_group in PLUGIN_GROUPS:
            plugin_group_info = self._get_group_info(plugin_group)
            for entry_point in pkg_resources.iter_entry_points(plugin_group):
                lazy_plugin = LazyEntryPointPlugin(entry_point)
                plugin_group_info["plugins"][entry_point.name] = lazy_plugin
            for entry_point in pkg_resources.iter_entry_points(plugin_group + ".suffixes"):
                lazy_plugin = LazyEntryPointPlugin(entry_point)
                plugin_group_info["suffixes"][entry_point.name] = lazy_plugin
