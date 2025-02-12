# CV Customization System

A comprehensive system for customizing and managing professional CVs for different target audiences using Cursor. This repository contains my CV in latex and the necessary tools/guidelines for effective customization with Cursor.

## 📁 Repository Structure

```
.
├── docs/
│   ├── CV.md                           # LLM-friendly CV version
│   ├── Target-Audiences-Taxonomy.md    # Comprehensive guide for different CV versions
│   └── Prompt-Engineering-Guidelines.md # AI prompting guidelines for CV customization
├── pdfs/                               # Compiled PDF files
├── fonts/                              # Fonts for the LaTeX template
├── tex/                                # LaTeX files
│   └── deedy-resume-openfont.cls       # LaTeX template
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- LaTeX distribution (e.g., TeX Live, MiKTeX) with XeLaTeX engine
- Cursor IDE

### Building the CV
1. Use the Makefile to compile the LaTeX files:
   ```bash
   make english
   make spanish
   ```

## 📖 Documentation

### CV Versions
The CV is maintained in multiple formats:
- **LaTeX** (`tex/`): For professional PDF output
- **Markdown** (`docs/CV.md`): LLM-friendly version for AI processing

### Customization Guidelines
- `Target-Audiences-Taxonomy.md`: Comprehensive guide for tailoring CVs to different industries and roles
- `Prompt-Engineering-Guidelines.md`: Best practices for using AI to assist in CV customization

## 🤝 Feel free to use or contribute

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Deedy Resume](https://github.com/deedy/Deedy-Resume) for the LaTeX template
- Contributors and maintainers of the LaTeX template and MikTeX distribution
- CursorAI for the AI tools and platforms used in the development process
