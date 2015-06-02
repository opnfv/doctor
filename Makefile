BUILDDIR = build
DESIGN_DOCS = $(wildcard design_docs/*.rst)

.PHONY: clean html pdf all

all: html pdf

clean:
	rm -rf $(BUILDDIR)/*

html: $(DESIGN_DOCS)
	mkdir -p build/design_docs
	rst2html.py $^ $(BUILDDIR)/$(^:.rst=.html)
	sphinx-build -b html -c etc -d $(BUILDDIR)/doctrees \
	    requirements $(BUILDDIR)/requirements/html

pdf:
	sphinx-build -b latex -c etc -d $(BUILDDIR)/doctrees \
	    requirements $(BUILDDIR)/requirements/latex
	$(MAKE) -C $(BUILDDIR)/requirements/latex \
	    LATEXOPTS='--interaction=batchmode' all-pdf
