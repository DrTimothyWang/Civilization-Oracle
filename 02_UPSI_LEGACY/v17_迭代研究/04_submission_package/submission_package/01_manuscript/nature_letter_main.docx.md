# Nature Letter Word Conversion Guide

**Source**: `nature_letter_main.md`  
**Target**: `nature_letter_main.docx` (Microsoft Word)  
**Date**: 2026-06-05

---

## Why Convert?

Nature's submission system accepts either:
- Microsoft Word (.docx) — **recommended for Letters**
- LaTeX (.tex + .pdf) — acceptable but slower editorial workflow

This guide explains how to convert the Markdown manuscript to a properly formatted Word document.

---

## Method 1: Pandoc (Recommended for Technical Users)

### Prerequisites
```bash
# macOS
brew install pandoc

# Ubuntu/Debian
sudo apt-get install pandoc

# Windows
# Download from https://pandoc.org/installing.html
```

### Conversion Command
```bash
cd /Users/wangzr/Desktop/历史事件预测建模/v17_迭代研究/04_submission_package/submission_package/01_manuscript

pandoc nature_letter_main.md \
  -o nature_letter_main.docx \
  --from markdown \
  --to docx \
  --reference-doc=nature_template.docx \
  --toc \
  --number-sections
```

> **Note**: `nature_template.docx` is a custom reference document with Nature formatting. If unavailable, omit `--reference-doc` and format manually after conversion.

### Post-Conversion Formatting Checklist
After pandoc conversion, open in Microsoft Word and verify:

- [ ] **Font**: Times New Roman, 11 pt (body); 12 pt bold (headings)
- [ ] **Line spacing**: 1.5 lines
- [ ] **Margins**: 2.5 cm (1 inch) all sides
- [ ] **Page size**: A4 or US Letter
- [ ] **Abstract**: 150 words, single paragraph, no subheadings
- [ ] **Headings**: Bold, sentence case (e.g., "Results" not "RESULTS")
- [ ] **Subheadings**: Italic, sentence case
- [ ] **References**: Numbered, Nature style (see below)
- [ ] **Figures**: Placeholder text only; upload figures separately
- [ ] **Tables**: Editable Word tables (not images)
- [ ] **Equations**: Microsoft Equation Editor or MathType

---

## Method 2: Typora + Manual Export (Recommended for Non-Technical Users)

1. **Install Typora**: https://typora.io/ (free trial available)
2. **Open** `nature_letter_main.md` in Typora
3. **Verify rendering**: Check that equations, tables, and citations display correctly
4. **Export**: File → Export → Word (.docx)
5. **Format in Word**: Apply Nature formatting as described above

---

## Method 3: Overleaf LaTeX (Alternative)

If you prefer LaTeX:

1. Go to https://www.overleaf.com/gallery/tagged/nature
2. Select **"Nature Letter"** template
3. Copy-paste sections from `nature_letter_main.md`
4. Upload figures from `figures/` directory
5. Compile to PDF
6. Submit both .tex source and .pdf

---

## Nature-Specific Formatting Rules

### Title
- Maximum 90 characters (including spaces)
- Our title: "A Cross-Domain Pressure Synchronization Index for Crisis Detection Across Civilizations" — **check length**

### Abstract
- 150 words maximum (Nature Letter)
- Single paragraph
- No references, no abbreviations, no equations
- Our abstract: 150 words ✅

### Main Text
- ~3,000 words (Nature Letter)
- Our main text: ~2,850 words ✅
- No more than 4–6 display items (figures + tables)
- We have 4 figures + 2 tables = 6 display items ✅

### Methods
- 800 words maximum (Nature Letter)
- Placed at end of main text
- Our Methods: ~800 words ✅

### References
- Maximum 30 references (Nature Letter)
- We have 25 references ✅
- Numbered sequentially
- Nature style:
  - Journal articles: Author(s). Title. *Journal* **Volume**, pages (Year).
  - Books: Author(s). *Title*. Publisher (Year).
  - Websites: Author/Organization. Title. URL (Date accessed).

### Figures
- Upload as separate files (not embedded in Word)
- Preferred formats: TIFF, EPS, PNG (300 dpi minimum)
- Maximum width: 180 mm (7 inches)
- Color figures: Nature charges $500+ for print color; online color is free
- **Recommendation**: Submit all figures in color for online; grayscale acceptable for print

### Tables
- Editable Word tables (not images)
- Place at end of manuscript or inline
- Our manuscript has 2 tables (Table 1: domain validation; Table 2: feature-engineered AUC)

---

## Equation Formatting

The manuscript contains two key equations:

### Equation 1: UPSI Definition
```
UPSI(t) = 0.4 × Material_z(t) + 0.3 × Fragmentation_z(t) + 0.3 × Disengagement_z(t)
```

In Word: Use Insert → Equation or type as plain text with subscripts.

### Equation 2: SPI Definition
```
SPI(t) = 0.35 × z(Velocity) + 0.25 × z(Acceleration) + 0.25 × |ΔGSI| + 0.15 × Volatility_Spike
```

In Word: Same approach.

---

## Common Conversion Issues

| Issue | Markdown | Word Fix |
|-------|----------|----------|
| Bold text | `**text**` | Verify bold formatting |
| Italic text | `*text*` | Verify italic formatting |
| Superscript | `^2` | Use superscript formatting |
| Subscript | `~z~` | Use subscript formatting |
| Tables | Markdown tables | Convert to Word tables |
| Footnotes | `[^1]` | Convert to endnotes or inline |
| Cross-references | `(Fig. 1)` | Verify figure numbering |

---

## Final Verification

Before uploading to Nature's submission system:

1. [ ] Open .docx in Microsoft Word (not Google Docs, not Pages)
2. [ ] Check word count: Tools → Word Count
3. [ ] Check figure/table count
4. [ ] Verify all citations are numbered 1–25
5. [ ] Spell-check: Tools → Spelling & Grammar
6. [ ] Save as .docx (not .doc)
7. [ ] File name: `UPSI_Nature_Letter_v17.docx`

---

## Upload Checklist (Nature Submission System)

- [ ] Manuscript: `UPSI_Nature_Letter_v17.docx`
- [ ] Cover letter: `cover_letter.docx`
- [ ] Figures: `fig1.png`, `fig2.png`, `fig3.png`, `fig4.png` (separate files)
- [ ] SI: `SI_v17.pdf` (assembled separately)
- [ ] Author contributions: included in manuscript
- [ ] Data availability: included in manuscript
- [ ] Code availability: included in manuscript
- [ ] Competing interests: included in manuscript

---

*Conversion guide prepared: 2026-06-05*
