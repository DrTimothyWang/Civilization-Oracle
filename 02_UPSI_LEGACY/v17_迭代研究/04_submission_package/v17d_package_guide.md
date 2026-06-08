# v17d Package Guide — Nature Letter Submission

**Version**: v17.0  
**Date**: 2026-06-05  
**Purpose**: Comprehensive guide for assembling and submitting the UPSI manuscript to *Nature* (Letter format)

---

## 1. What's in Each Directory

### `01_manuscript/` — Main Text & Figures
- `nature_letter_main.md` — Full Nature Letter manuscript (v14 base, ~2,850 words main text + 150 abstract + 800 Methods)
- `nature_letter_main.docx` — Conversion guide (see §3 below)
- `pnas_backup.md` — PNAS 6-page backup manuscript (if Nature rejects or requests transfer)
- `figures/` — 4 main-text figures + 1 SI candidate:
  - `figure1_domain_validation.png` — Cross-domain validation across 7 civilizations
  - `figure2_psi_spi_duality.png` — PSI+SPI phase portrait (mathematical duality)
  - `figure3_upsi_v2_quadrants.png` — Four-quadrant crisis classifier
  - `figure4_dashboard.png` — Real-time UPSI Dashboard screenshot
  - `figure5_seshat_map.png` — Seshat NGA coverage map (SI candidate; see note below)

> **Note on figure5**: No static map PNG exists in the current iteration. The Seshat validation uses 5 NGAs (Upper Egypt, Latium, Susiana, Middle Yellow River Valley, Valley of Oaxaca). For submission, either (a) generate a world map with NGA markers, or (b) omit and reference Seshat validation in text only. See `v17d_figure_selection.md` for detailed caption drafts.

### `02_supplementary/` — Supplementary Information (SI)
- `si_master.md` — Master assembly guide for all 22 SI sections
- `s1_domain_operationalization.md` through `s22_code_data_availability.md` — Placeholder/reference files pointing to source materials across v4–v16 iteration directories

> **Important**: The SI content is scattered across 17 iteration directories. The `si_master.md` file contains instructions for locating and assembling each section. Do NOT attempt to copy all SI content into this package—it would exceed 50 MB. Instead, assemble the SI after manuscript acceptance.

### `03_cover_letter/` — Submission Letter
- `cover_letter.md` — Nature cover letter (v15d base)
- `highlighted_references.md` — 17 highlighted references with justification for each
- `suggested_reviewers.md` — 5 suggested reviewers + 2 opposed reviewers

### `04_author_materials/` — Administrative Documents
- `author_contributions.md` — CRediT-style author contributions
- `data_availability.md` — Data availability statement (all public APIs)
- `code_availability.md` — Code availability statement (GitHub repo upon publication)
- `competing_interests.md` — Competing interests declaration (none)

### `05_reviewer_prep/` — Pre-Submission Reviewer Preparation
- `anticipated_qa.md` — 18 anticipated reviewer questions + honest answers (from v14_reviewer_QA.md)
- `preemptive_fixes.md` — Changes already made in response to anticipated critiques
- `risk_assessment.md` — Risk matrix for submission (acceptance probability, revision scenarios)

### `06_dashboard/` — Real-Time Monitoring System
- `dashboard_repo/` — Complete deployable dashboard (GitHub Actions + gh-pages, MIT license)
- `deployment_guide.md` — Step-by-step deployment instructions
- `local_test_results.json` — Local test results (19/20 assets pass)

### `07_code/` — Core Computation Scripts
- `psi_engine.py` — Domain-agnostic PSI calculator (from v6/global_upsi_v6.py)
- `spi_engine.py` — Sudden Pressure Indicator for burst-crisis detection (from v13b_spi_formula.py)
- `upsi_v2.py` — Four-quadrant state-space classifier (from v14c_upsi_v2.py)
- `seshat_psi.py` — Seshat-to-UPSI variable mapping (from v14a_seshat_psi_engine.py)
- `requirements.txt` — Pinned Python dependencies

### `08_data_samples/` — Reviewer-Inspectable Data
- `chinese_history_psi.json` — Sample CBDB-derived PSI (decade-level, Tang dynasty)
- `mesopotamia_psi.json` — Sample CDLI/ORACC SFD proxy validation summary
- `global_finance_psi.json` — Sample global finance PSI (blind test results)
- `seshat_psi.json` — Sample Seshat NGA data (5 polities, 337 centuries)

---

## 2. How to Convert .md to .docx for Submission

Nature accepts Word (.docx) or LaTeX submissions. For Word:

### Option A: Pandoc (Recommended)
```bash
# Install pandoc if not already installed
brew install pandoc  # macOS

# Convert main manuscript
pandoc nature_letter_main.md \
  -o nature_letter_main.docx \
  --reference-doc=nature_template.docx \
  --citeproc \
  --bibliography=references.bib

# Convert cover letter
pandoc cover_letter.md -o cover_letter.docx
```

### Option B: Manual Copy-Paste
1. Open `nature_letter_main.md` in a Markdown editor (Typora, VS Code)
2. Copy the rendered text
3. Paste into Microsoft Word
4. Apply Nature Letter formatting:
   - Font: Times New Roman, 11 pt
   - Line spacing: 1.5
   - Margins: 2.5 cm all sides
   - Abstract: 150 words, single paragraph
   - Main text: ~2,850 words, 4 pages
   - Methods: 800 words, separate section

### Option C: Overleaf (LaTeX)
If you prefer LaTeX, use the Nature Letter template on Overleaf:
1. Go to overleaf.com/gallery/tagged/nature
2. Select "Nature Letter" template
3. Copy-paste sections from `nature_letter_main.md`
4. Upload figures from `01_manuscript/figures/`

---

## 3. How to Assemble SI from Scattered Files

The SI spans 22 sections across 17 iteration directories. Follow this workflow:

### Step 1: Use `si_master.md` as the index
Open `02_supplementary/si_master.md`. It contains:
- Section number and title
- Source file path (e.g., `v4/bayesian_prediction_v4.py` for S3)
- Assembly instructions (copy, summarize, or reference)

### Step 2: Create a working SI directory
```bash
mkdir ~/UPSI_SI_v17
cd ~/UPSI_SI_v17
```

### Step 3: Assemble each section
For each section in `si_master.md`:
- **If source is a .md file**: Copy and renumber headers
- **If source is a .py file**: Extract docstrings and key functions into a code listing
- **If source is a .json file**: Include a formatted table or sample
- **If source is a figure**: Copy PNG and write caption

### Step 4: Compile into a single PDF
Use pandoc or LaTeX to compile all sections:
```bash
pandoc s1.md s2.md ... s22.md -o SI_v17.pdf --toc
```

### Step 5: Verify completeness
Check against the SI completeness checklist in `v17d_submission_checklist.md`.

---

## 4. How to Zip the Package for Upload

### Create the zip archive
```bash
cd /Users/wangzr/Desktop/历史事件预测建模/v17_迭代研究/04_submission_package/
zip -r UPSI_v17_submission_package.zip submission_package/ \
  -x "*.DS_Store" -x "*__pycache__*" -x "*.git*"
```

### Verify size
```bash
du -sh UPSI_v17_submission_package.zip
# Should be < 50 MB
```

### Upload to Nature Submission System
1. Go to [nature.com/nature/for-authors/submit](https://www.nature.com/nature/for-authors/submit)
2. Select **Letter** format
3. Upload files:
   - Manuscript: `nature_letter_main.docx`
   - Figures: `figure1.png` through `figure4.png` (separate files, 300 dpi)
   - Cover letter: `cover_letter.docx`
   - SI: `SI_v17.pdf` (assembled separately)
   - Data availability: included in manuscript

---

## 5. Pre-Submission Checklist (Summary)

See `v17d_submission_checklist.md` for the full checklist. Key items:

- [ ] Word count ≤ 3,000 (main text) + 150 (abstract) + 800 (Methods)
- [ ] Figures ≤ 6 (Nature Letter max; we have 4 main + 1 SI candidate)
- [ ] References ≤ 30 (Nature limit; we have 25)
- [ ] SI sections = 22 (all listed in `si_master.md`)
- [ ] Data availability statement included
- [ ] Code availability statement included
- [ ] Author contributions included
- [ ] Competing interests declared (none)
- [ ] Cover letter uploaded
- [ ] Suggested reviewers provided (5)
- [ ] Figure captions drafted (see `v17d_figure_selection.md`)
- [ ] All figures at 300 dpi minimum
- [ ] Package size < 50 MB

---

## 6. Post-Submission Workflow

### If accepted without revision
1. Assemble full SI from scattered files
2. Upload code to GitHub (github.com/Mavis-Foundation/UPSI)
3. Publish data samples on Zenodo
4. Update Dashboard to production URL

### If minor revision requested
1. Address reviewer comments using `05_reviewer_prep/anticipated_qa.md`
2. Update manuscript in `01_manuscript/nature_letter_main.md`
3. Re-export to .docx
4. Resubmit within 4 weeks

### If major revision requested
1. Convene team meeting to prioritize changes
2. Update relevant SI sections
3. Consider additional validation (e.g., Seshat expansion to 10+ NGAs)
4. Resubmit within 8 weeks

### If rejected
1. Evaluate reviewer feedback for PNAS transfer
2. Use `pnas_backup.md` as starting point
3. Adjust to PNAS 6-page format
4. Submit to PNAS within 2 weeks

---

## 7. Contact & Support

**Corresponding author**: Wang Dianrang (wangdianrang@gzhmu.edu.cn)  
**Technical lead**: Mavis Agent Team  
**Repository**: github.com/Mavis-Foundation/UPSI (upon publication)

---

*This guide is part of the v17 submission package. For questions, refer to the iteration history in v1–v16 directories.*
