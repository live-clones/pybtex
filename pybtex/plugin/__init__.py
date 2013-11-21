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

from pybtex.utils import deprecated


class Plugin(object):
    name = None
    aliases = ()
    suffixes = ()  # first is default

    @classmethod
    def get_default_suffix(cls):
        if cls.suffixes:
            return cls.suffixes[0]
        else:
            return None


def find_plugin(plugin_group, name=None, filename=None):
    from pybtex.plugin.loader import plugin_loader
    return plugin_loader.find_plugin(
        plugin_group, name=name, filename=filename)


def enumerate_plugin_names(plugin_group):
    from pybtex.plugin.loader import plugin_loader
    return plugin_loader.enumerate_plugin_names(plugin_group)


def register_plugin(plugin_group, plugin_class):
    from pybtex.plugin.loader import plugin_loader
    return plugin_loader.register_plugin(plugin_group, plugin_class)
