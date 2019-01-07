# makefile for sphinx documentation
#

# you can set these variables from the command line.
sphinxopts    =
sphinxbuild   = sphinx-build
paper         =
builddir      = build

# user-friendly check for sphinx-build
ifeq ($(shell which $(sphinxbuild) >/dev/null 2>&1; echo $$?), 1)
$(error the '$(sphinxbuild)' command was not found. make sure you have sphinx installed, then set the sphinxbuild environment variable to point to the full path of the '$(sphinxbuild)' executable. alternatively you can add the directory with the executable to your path. if you don't have sphinx installed, grab it from http://sphinx-doc.org/)
endif

# internal variables.
paperopt_a4     = -d latex_paper_size=a4
paperopt_letter = -d latex_paper_size=letter
allsphinxopts   = -d $(builddir)/doctrees $(paperopt_$(paper)) $(sphinxopts) source
sitesphinxopts   = -d $(builddir)/site-doctrees $(paperopt_$(paper)) $(sphinxopts) site
# the i18n builder cannot share the environment and doctrees with the others
i18nsphinxopts  = $(paperopt_$(paper)) $(sphinxopts) source

.PHONY: help clean html site dirhtml singlehtml pickle json htmlhelp qthelp devhelp epub latex latexpdf text man changes linkcheck doctest gettext upload-docs upload-site upload

help:
	@echo "please use \`make <target>' where <target> is one of"
	@echo "  html       to make standalone html files"
	@echo "  dirhtml    to make html files named index.html in directories"
	@echo "  singlehtml to make a single large html file"
	@echo "  pickle     to make pickle files"
	@echo "  json       to make json files"
	@echo "  htmlhelp   to make html files and a html help project"
	@echo "  qthelp     to make html files and a qthelp project"
	@echo "  devhelp    to make html files and a devhelp project"
	@echo "  epub       to make an epub"
	@echo "  latex      to make latex files, you can set paper=a4 or paper=letter"
	@echo "  latexpdf   to make latex files and run them through pdflatex"
	@echo "  latexpdfja to make latex files and run them through platex/dvipdfmx"
	@echo "  text       to make text files"
	@echo "  man        to make manual pages"
	@echo "  texinfo    to make texinfo files"
	@echo "  info       to make texinfo files and run them through makeinfo"
	@echo "  gettext    to make po message catalogs"
	@echo "  changes    to make an overview of all changed/added/deprecated items"
	@echo "  xml        to make docutils-native xml files"
	@echo "  pseudoxml  to make pseudoxml-xml files for display purposes"
	@echo "  linkcheck  to check all external links for integrity"
	@echo "  doctest    to run all doctests embedded in the documentation (if enabled)"

clean:
	rm -rf $(builddir)/*

html:
	$(sphinxbuild) -b html $(allsphinxopts) $(builddir)/html
	@echo
	@echo "build finished. the html pages are in $(builddir)/html."

site:
	$(sphinxbuild) -b html $(sitesphinxopts) $(builddir)/site
	@echo
	@echo "build finished. the site pages are in $(builddir)/site."

dirhtml:
	$(sphinxbuild) -b dirhtml $(allsphinxopts) $(builddir)/dirhtml
	@echo
	@echo "build finished. the html pages are in $(builddir)/dirhtml."

singlehtml:
	$(sphinxbuild) -b singlehtml $(allsphinxopts) $(builddir)/singlehtml
	@echo
	@echo "build finished. the html page is in $(builddir)/singlehtml."

pickle:
	$(sphinxbuild) -b pickle $(allsphinxopts) $(builddir)/pickle
	@echo
	@echo "build finished; now you can process the pickle files."

json:
	$(sphinxbuild) -b json $(allsphinxopts) $(builddir)/json
	@echo
	@echo "build finished; now you can process the json files."

htmlhelp:
	$(sphinxbuild) -b htmlhelp $(allsphinxopts) $(builddir)/htmlhelp
	@echo
	@echo "build finished; now you can run html help workshop with the" \
	      ".hhp project file in $(builddir)/htmlhelp."

qthelp:
	$(sphinxbuild) -b qthelp $(allsphinxopts) $(builddir)/qthelp
	@echo
	@echo "build finished; now you can run "qcollectiongenerator" with the" \
	      ".qhcp project file in $(builddir)/qthelp, like this:"
	@echo "# qcollectiongenerator $(builddir)/qthelp/pybtex.qhcp"
	@echo "to view the help file:"
	@echo "# assistant -collectionfile $(builddir)/qthelp/pybtex.qhc"

devhelp:
	$(sphinxbuild) -b devhelp $(allsphinxopts) $(builddir)/devhelp
	@echo
	@echo "build finished."
	@echo "to view the help file:"
	@echo "# mkdir -p $$home/.local/share/devhelp/pybtex"
	@echo "# ln -s $(builddir)/devhelp $$home/.local/share/devhelp/pybtex"
	@echo "# devhelp"

epub:
	$(sphinxbuild) -b epub $(allsphinxopts) $(builddir)/epub
	@echo
	@echo "build finished. the epub file is in $(builddir)/epub."

latex:
	$(sphinxbuild) -b latex $(allsphinxopts) $(builddir)/latex
	@echo
	@echo "build finished; the latex files are in $(builddir)/latex."
	@echo "run \`make' in that directory to run these through (pdf)latex" \
	      "(use \`make latexpdf' here to do that automatically)."

latexpdf:
	$(sphinxbuild) -b latex $(allsphinxopts) $(builddir)/latex
	@echo "running latex files through pdflatex..."
	$(make) -c $(builddir)/latex all-pdf
	@echo "pdflatex finished; the pdf files are in $(builddir)/latex."

latexpdfja:
	$(sphinxbuild) -b latex $(allsphinxopts) $(builddir)/latex
	@echo "running latex files through platex and dvipdfmx..."
	$(make) -c $(builddir)/latex all-pdf-ja
	@echo "pdflatex finished; the pdf files are in $(builddir)/latex."

text:
	$(sphinxbuild) -b text $(allsphinxopts) $(builddir)/text
	@echo
	@echo "build finished. the text files are in $(builddir)/text."

man:
	$(sphinxbuild) -b man $(allsphinxopts) $(builddir)/man
	@echo
	@echo "build finished. the manual pages are in $(builddir)/man."

texinfo:
	$(sphinxbuild) -b texinfo $(allsphinxopts) $(builddir)/texinfo
	@echo
	@echo "build finished. the texinfo files are in $(builddir)/texinfo."
	@echo "run \`make' in that directory to run these through makeinfo" \
	      "(use \`make info' here to do that automatically)."

info:
	$(sphinxbuild) -b texinfo $(allsphinxopts) $(builddir)/texinfo
	@echo "running texinfo files through makeinfo..."
	make -c $(builddir)/texinfo info
	@echo "makeinfo finished; the info files are in $(builddir)/texinfo."

gettext:
	$(sphinxbuild) -b gettext $(i18nsphinxopts) $(builddir)/locale
	@echo
	@echo "build finished. the message catalogs are in $(builddir)/locale."

changes:
	$(sphinxbuild) -b changes $(allsphinxopts) $(builddir)/changes
	@echo
	@echo "the overview file is in $(builddir)/changes."

linkcheck: linkcheck-site linkcheck-docs

linkcheck-docs:
	$(sphinxbuild) -b linkcheck $(allsphinxopts) $(builddir)/linkcheck
	@echo
	@echo "link check complete; look for any errors in the above output " \
	      "or in $(builddir)/linkcheck/output.txt."

linkcheck-site:
	$(sphinxbuild) -b linkcheck $(sitesphinxopts) $(builddir)/linkcheck
	@echo
	@echo "link check complete; look for any errors in the above output " \
	      "or in $(builddir)/linkcheck/output.txt."

doctest:
	$(sphinxbuild) -b doctest $(allsphinxopts) $(builddir)/doctest
	@echo "testing of doctests in the sources finished, look at the " \
	      "results in $(builddir)/doctest/output.txt."

xml:
	$(sphinxbuild) -b xml $(allsphinxopts) $(builddir)/xml
	@echo
	@echo "build finished. the xml files are in $(builddir)/xml."

pseudoxml:
	$(sphinxbuild) -b pseudoxml $(allsphinxopts) $(builddir)/pseudoxml
	@echo
	@echo "build finished. the pseudo-xml files are in $(builddir)/pseudoxml."


# https://pybtex.org/ stuff
RSYNC = rsync -rv --delete
RSYNC_SERVER = www-pybtex@pybtex.org

upload-docs: html
	$(RSYNC) $(builddir)/html/ $(RSYNC_SERVER):docs/html/

upload-site: site
	$(RSYNC) $(builddir)/site/ $(RSYNC_SERVER):www/html/

upload: upload-site upload-docs
