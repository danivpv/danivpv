# Directory structure
TEX_DIR = tex
TMP_DIR = tex/.build
PDF_DIR = pdfs
APP_DIR = applications

.PHONY: tex-to-pdf md-to-pdf cv letter clean

# ─── Core tasks ─────────────────────────────────────────────

tex-to-pdf:
	mkdir -p $(TMP_DIR) $(out)
	xelatex -aux-directory=$(TMP_DIR) \
	        -output-directory=$(out) \
	        $(src)

md-to-pdf:
	pandoc $(src) -o $(out) --pdf-engine=xelatex

# ─── Use case tasks ─────────────────────────────────────────

cv:
ifdef role
ifdef company
	$(error Cannot specify both role and company)
endif
	$(MAKE) tex-to-pdf src=$(TEX_DIR)/$(role).tex out=$(PDF_DIR)
else ifdef company
	$(MAKE) tex-to-pdf src=$(APP_DIR)/$(company)/cv.tex out=$(APP_DIR)/$(company)
else
	$(error Must specify either role or company)
endif

letter:
	$(MAKE) md-to-pdf \
	        src=$(APP_DIR)/$(company)/$(role)_cover_letter.md \
	        out=$(APP_DIR)/$(company)/$(role)_cover_letter.pdf

# ─── Clean ──────────────────────────────────────────────────

clean:
	rm -rf $(TMP_DIR)/* $(PDF_DIR)/*