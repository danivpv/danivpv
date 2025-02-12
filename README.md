# CV Customization System

A comprehensive system for customizing and managing professional CVs for different target audiences using AI-assisted workflows. This repository contains both the CV content and the necessary tools/guidelines for effective customization.

## 🎯 Purpose

This repository serves as a central hub for:
1. Managing CV content in multiple formats (LaTeX, Markdown)
2. Providing guidelines for CV customization
3. Documenting best practices for AI-assisted CV optimization
4. Maintaining version control for different target audiences

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
- Python for automation scripts (if any)
- Text editor or IDE (VS Code recommended)

### Building the CV
1. Use the Makefile to compile the LaTeX files:
   ```bash
   make
   ```

## 📖 Documentation

### CV Versions
The CV is maintained in multiple formats:
- **LaTeX** (`tex/`): Professional PDF output
- **Markdown** (`docs/CV.md`): LLM-friendly version for AI processing

### Customization Guidelines
- `Target-Audiences-Taxonomy.md`: Comprehensive guide for tailoring CVs to different industries and roles
- `Prompt-Engineering-Guidelines.md`: Best practices for using AI to assist in CV customization

## 🛠️ Usage

### Manual Customization
1. Choose target audience from `Target-Audiences-Taxonomy.md`
2. Edit relevant sections in LaTeX/Markdown
3. Compile to generate new PDF

### AI-Assisted Customization
1. Reference `Prompt-Engineering-Guidelines.md`
2. Use provided prompts with your preferred LLM
3. Review and incorporate AI suggestions
4. Update source files and compile

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Deedy Resume](https://github.com/deedy/Deedy-Resume) for the LaTeX template
- Contributors and maintainers of the LaTeX template
- AI tools and platforms used in the development process
