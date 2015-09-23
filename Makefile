BUILDDIR := build
PUBLICDIR := public
DESIGN_DOCS = $(wildcard design_docs/*.rst)
MANUALS = $(wildcard manuals/*.rst)

.PHONY: clean html pdf bps man all public

define index
	rm -f $1/index.html
	find $1 -type f | while read a; do echo "<li><a href=$${a#$1/}>$${a#$1/}</a></li>" >> $1/index.html; done
endef

all: man bps html pdf
	$(call index,$(BUILDDIR))

public:
	rm -rf $(PUBLICDIR)
	mkdir -p $(PUBLICDIR)
	cp -r $(BUILDDIR)/manuals $(PUBLICDIR)/
	cp -r $(BUILDDIR)/design_docs $(PUBLICDIR)/
	cp -r $(BUILDDIR)/requirements/html $(PUBLICDIR)/
	cp -r $(BUILDDIR)/requirements/latex/*.pdf $(PUBLICDIR)/
	$(call index,$(PUBLICDIR))

clean:
	rm -rf $(BUILDDIR)/*

man:
	mkdir -p $(BUILDDIR)/manuals
	$(foreach f,$(MANUALS),rst2html.py $(f) $(BUILDDIR)/$(f:.rst=.html);)

bps: $(DESIGN_DOCS)
	mkdir -p $(BUILDDIR)/design_docs
	$(foreach f,$(DESIGN_DOCS),rst2html.py $(f) $(BUILDDIR)/$(f:.rst=.html);)

html:
	sphinx-build -b html -c etc -d $(BUILDDIR)/doctrees \
	    requirements $(BUILDDIR)/requirements/html

pdf:
	sphinx-build -b latex -c etc -d $(BUILDDIR)/doctrees \
	    requirements $(BUILDDIR)/requirements/latex
	$(MAKE) -C $(BUILDDIR)/requirements/latex \
	    LATEXOPTS='--interaction=nonstopmode' all-pdf
