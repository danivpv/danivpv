# Directory structure
TEX_DIR = tex
TMP_DIR = tmp
PDF_DIR = pdfs

# Ensure output directories exist
$(shell mkdir -p $(TMP_DIR) $(PDF_DIR))

# Default compiler
LATEX = xelatex

# Common compiler flags
FLAGS = -aux-directory=$(TMP_DIR) -output-directory=$(PDF_DIR)

# Specific targets
.PHONY: clean english spanish

english:
	$(LATEX) $(FLAGS) $(TEX_DIR)/english.tex

spanish:
	$(LATEX) $(FLAGS) $(TEX_DIR)/spanish.tex

# Clean temporary files
clean:
	rm -rf $(TMP_DIR)/* $(PDF_DIR)/*