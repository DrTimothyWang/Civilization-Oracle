# UPSI Submission Package — v17.0

**Project**: Unified Pressure Synchronization Index (UPSI) for Cross-Domain Crisis Detection  
**Target Journal**: *Nature* (Letter, 4 pages)  
**Backup Target**: *PNAS* (6 pages)  
**Date**: 2026-06-05  
**Version**: v17.0 (17 iterations, 5,500 years, 7+ domains)

---

## Package Structure

```
submission_package/
├── 01_manuscript/          # Main text + figures for Nature Letter
├── 02_supplementary/       # SI assembly guide + S1-S22 references
├── 03_cover_letter/        # Cover letter + highlighted refs + suggested reviewers
├── 04_author_materials/    # Author contributions, data/code availability, COI
├── 05_reviewer_prep/       # Anticipated Q&A, preemptive fixes, risk assessment
├── 06_dashboard/           # Deployable dashboard repo + deployment guide
├── 07_code/                # Key computation scripts (PSI, SPI, UPSI_v2, Seshat)
├── 08_data_samples/        # Sample JSON data for reviewer inspection
└── README.md               # This file
```

---

## Quick Start

1. **Read the manuscript**: `01_manuscript/nature_letter_main.md`
2. **Check the checklist**: `../v17d_submission_checklist.md`
3. **Follow the guide**: `../v17d_package_guide.md`
4. **Inspect figures**: `01_manuscript/figures/` (4 main + 1 SI candidate)
5. **Review code**: `07_code/` (4 core Python modules + requirements.txt)

---

## Key Metrics at a Glance

| Metric | Value |
|--------|-------|
| Main text word count | ~2,850 words |
| Abstract | 150 words |
| Methods | 800 words |
| Figures (main text) | 4 |
| References | 25 (Nature style) |
| SI sections | 22 |
| Domains validated | 8 (7 original + Seshat) |
| Total observations | ~3.6 million |
| Time span | 5,500 years |
| Recall range | 75% – 100% |

---

## File Size Budget

| Directory | Approx. Size |
|-----------|-------------|
| 01_manuscript | ~2 MB (figures) |
| 02_supplementary | ~100 KB (text only) |
| 03_cover_letter | ~50 KB |
| 04_author_materials | ~50 KB |
| 05_reviewer_prep | ~100 KB |
| 06_dashboard | ~100 KB (repo, no node_modules) |
| 07_code | ~200 KB |
| 08_data_samples | ~200 KB |
| **Total** | **< 5 MB** |

The full package is well under the 50 MB limit. Large datasets (>10 MB) are referenced externally, not included.

---

## Contact

**Corresponding author**: Wang Dianrang  
**Email**: wangdianrang@gzhmu.edu.cn  
**Affiliation**: Guangzhou University of Chinese Medicine  
**Team**: Mavis Agent Team, Mavis AI Foundation

---

*Prepared for Nature Letter submission. All materials are original and have not been published elsewhere.*
