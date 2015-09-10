BUILDDIR := build
DESIGN_DOCS = $(wildcard design_docs/*.rst)
MANUALS = $(wildcard manuals/*.rst)

.PHONY: clean html pdf bps man all

all: man bps html pdf

clean:
	rm -rf $(BUILDDIR)/*

man: | $(BUILDDIR)	
	mkdir -p $(BUILDDIR)/manuals
	$(foreach f,$(MANUALS),rst2html.py $(f) $(BUILDDIR)/$(f:.rst=.html);)

bps: $(DESIGN_DOCS) | $(BUILDDIR)
	mkdir -p $(BUILDDIR)/design_docs
	$(foreach f,$(DESIGN_DOCS),rst2html.py $(f) $(BUILDDIR)/$(f:.rst=.html);)

html: | $(BUILDDIR)
	sphinx-build -b html -c etc -d $(BUILDDIR)/doctrees \
	    requirements $(BUILDDIR)/requirements/html

pdf: | $(BUILDDIR)
	sphinx-build -b latex -c etc -d $(BUILDDIR)/doctrees \
	    requirements $(BUILDDIR)/requirements/latex
	$(MAKE) -C $(BUILDDIR)/requirements/latex \
	    LATEXOPTS='--interaction=nonstopmode' all-pdf

$(BUILDDIR):
	mkdir -p $(BUILDDIR)
