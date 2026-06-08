"""
ORACC Data Fetcher for Civilization-Oracle Cross-Civilizational Validation
Version: v1.0 (2026-06-04)

Pulls cuneiform data from ORACC (Open Richly Annotated Cuneiform Corpus, Penn Museum)
and the ePSD2 (electronic Pennsylvania Sumerian Dictionary) bulk JSON downloads.

ORACC JSON documentation:
  http://oracc.museum.upenn.edu/doc/opendata/json/index.html

Each project (e.g., dcclt, riao, etcsri) provides a /json/{project}.zip bulk archive
containing catalogue.json, corpus.json, and corpusjson/{P-id}.json per-text files.

ePSD2 subproject archives (admin corpora + literature + practical texts):
  https://oracc.museum.upenn.edu/json/epsd2-admin-ur3.zip    # Ur III admin (largest)
  https://oracc.museum.upenn.edu/json/epsd2-admin-ed12.zip
  https://oracc.museum.upenn.edu/json/epsd2-admin-ed3a.zip
  https://oracc.museum.upenn.edu/json/epsd2-admin-ed3b.zip
  https://oracc.museum.upenn.edu/json/epsd2-admin-oakk.zip
  https://oracc.museum.upenn.edu/json/epsd2-admin-lagash2.zip
  https://oracc.museum.upenn.edu/json/epsd2-literary.zip
  https://oracc.museum.upenn.edu/json/epsd2-royal.zip
  https://oracc.museum.upenn.edu/json/epsd2-earlylit.zip
  https://oracc.museum.upenn.edu/json/epsd2-praxis.zip
  https://oracc.museum.upenn.edu/json/epsd2-praxis-udughul.zip
  https://oracc.museum.upenn.edu/json/epsd2-praxis-liturgy.zip
  https://oracc.museum.upenn.edu/json/epsd2-praxis-varia.zip

Pleiades geographic enrichment: http://api.pleiades.stoa.org/places/{id}/json

For UPSI cross-civilizational validation, this module:
  1. Downloads ORACC ZIP archives (resumable, with SSL skip option)
  2. Extracts catalogue.json (with period, provenience, pleiades_id, genre, language)
  3. Optionally extracts per-text corpusjson for transliteration + lemmatization
  4. Maps to UPSI period/genre vocabulary
  5. Optionally enriches with Pleiades geographic coordinates
  6. Emits a single oracc_catalog.csv (one row per text) for PSI computation
"""

import os
import io
import json
import csv
import time
import gzip
import zipfile
import logging
import argparse
import urllib.request
import urllib.error
import ssl
from collections import Counter, defaultdict
from typing import Optional, Iterator
from dataclasses import dataclass, asdict, field

# Quiet logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("oracc")


# ORACC projects and bulk download sizes (verified 2026-06-04 via HEAD requests)
# Format: short_name -> (zip_path, approx_size_mb, description)
ORACC_PROJECTS = {
    # General cuneiform corpora
    "dcclt":    ("/json/dcclt.zip", 73,
                 "Digital Corpus of Cuneiform Lexical Texts (10,215 texts, mainly Old Babylonian Nippur)"),
    "riao":     ("/json/riao.zip", 18,
                 "Royal Inscriptions of Assyria online (Assyrian kings 2334-609 BC)"),
    "rinap":    ("/json/rinap.zip", 24,
                 "Royal Inscriptions of Neo-Assyrian Period (744-609 BC)"),
    "saao":     ("/json/saao.zip", 66,
                 "State Archives of Assyria Online (Neo-Assyrian letters/omens)"),
    "etcsri":   ("/json/etcsri.zip", 13,
                 "Electronic Text Corpus of Sumerian Royal Inscriptions"),
    # ePSD2 sub-corpora (Penn Sumerian Dictionary)
    "epsd2":        ("/json/epsd2.zip", 213,
                     "ePSD2 main glossary + signlist (16k words, 50k names)"),
    "epsd2-ur3":    ("/json/epsd2-admin-ur3.zip", 562,
                     "ePSD2/CDLI Ur III administrative corpus (largest, ~2,940 admin texts)"),
    "epsd2-ed12":   ("/json/epsd2-admin-ed12.zip", 0.4,
                     "Early Dynastic I-II admin"),
    "epsd2-ed3a":   ("/json/epsd2-admin-ed3a.zip", 7,
                     "ED IIIa admin"),
    "epsd2-ed3b":   ("/json/epsd2-admin-ed3b.zip", 35,
                     "ED IIIb admin"),
    "epsd2-oakk":   ("/json/epsd2-admin-oakk.zip", 30,
                     "Old Akkadian admin"),
    "epsd2-lagash2":("//json/epsd2-admin-lagash2.zip", 5,
                     "Lagash II admin (Gudea period)"),
    "epsd2-lit":    ("/json/epsd2-literary.zip", 40,
                     "Old Babylonian Sumerian literary"),
    "epsd2-royal":  ("/json/epsd2-royal.zip", 15,
                     "Sumerian royal inscriptions"),
    "epsd2-early":  ("/json/epsd2-earlylit.zip", 1,
                     "Early Sumerian literature"),
    "epsd2-praxis": ("/json/epsd2-praxis.zip", 6,
                     "Incantations"),
    "epsd2-udughul":("/json/epsd2-praxis-udughul.zip", 2,
                     "Udughul (evil spirit) texts"),
    "epsd2-liturgy":("/json/epsd2-praxis-liturgy.zip", 3,
                     "Liturgies"),
    "epsd2-varia":  ("/json/epsd2-praxis-varia.zip", 0.1,
                     "Practical varia"),
}

# Period name -> approximate start year (BCE; negative = BCE)
# For PSI time-window assignment
PERIOD_TO_YEAR = {
    "Uruk IV":      -3350, "Uruk III":    -3100,
    "Jemdet Nasr":  -3100,
    "ED I-II":      -2900, "Early Dynastic I-II": -2900,
    "ED IIIa":      -2600, "Early Dynastic IIIa": -2600,
    "ED IIIb":      -2350, "Early Dynastic IIIb": -2350,
    "Ebla":         -2350,
    "Old Akkadian": -2334, "Old Akkadian; Ur III": -2200,
    "Ur III":       -2112,
    "Lagash II":    -2130, "Lagaš II":    -2130,
    "Old Assyrian": -2000,
    "Old Babylonian":    -1894,
    "Middle Assyrian":   -1392,
    "Middle Babylonian": -1595,
    "Neo-Assyrian":      -911,
    "Neo-Babylonian":    -626,
    "Late Babylonian":   -539,
    "Achaemenid":        -550, "Persian": -550,
    "Hellenistic":       -323,
    "First Millennium":  -1000,
    "Archaic":            -3000,
    "uncertain":          None, "unknown": None, "": None,
}

# Genre -> PSI-relevant category
GENRE_TO_CATEGORY = {
    "Administrative":  "ADMIN",     # Economic/transactional texts
    "Legal":           "LEGAL",     # Court records, contracts
    "Letter":          "COMM",      # Communications
    "Literary":        "LITERARY", # Cultural narratives
    "Lexical":         "LEXICAL",   # Word lists, vocabularies
    "School":          "EDU",       # Scribal education
    "Mathematical":    "TECH",      # Math/astronomy
    "Ritual":          "RITUAL",
    "Prayer/Incantation": "RITUAL",
    "Royal":           "ROYAL",     # Royal inscriptions
    "Scientific":      "TECH",
    "Divinatory":      "OMEN",      # Omens
    "unknown":         "OTHER",
}

ORACC_BASE = "https://oracc.museum.upenn.edu"


@dataclass
class OraccText:
    """Single cuneiform text record (normalized for PSI)."""
    p_number: str          # ORACC/CDLI composite ID (e.g., P121474)
    project: str           # Source project (e.g., dcclt, epsd2/admin/ur3)
    designation: str = "" # Publication designation (e.g., NATN 777)
    museum_no: str = ""
    collection: str = ""
    provenience: str = ""
    pleiades_id: str = ""
    lat: Optional[float] = None
    lon: Optional[float] = None
    period: str = ""
    period_year_start: Optional[int] = None
    language: str = ""
    genre: str = ""
    genre_category: str = ""
    subgenre: str = ""
    supergenre: str = ""
    material: str = ""
    object_type: str = ""
    has_atf: bool = False
    has_lem: bool = False
    has_tr_en: bool = False  # English translation
    publication_date: str = ""
    primary_publication: str = ""


class OraccFetcher:
    """Fetcher for ORACC + ePSD2 bulk JSON data, plus Pleiades geo enrichment."""

    def __init__(self, output_dir: str, skip_ssl: bool = True, user_agent: str = "Civilization-Oracle/1.0"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.cache_dir = os.path.join(output_dir, "oracc_cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        if skip_ssl:
            self._ctx = ssl.create_default_context()
            self._ctx.check_hostname = False
            self._ctx.verify_mode = ssl.CERT_NONE
        else:
            self._ctx = ssl.create_default_context()
        self._ua = user_agent
        # Pleiades in-memory cache
        self._pleiades_cache: dict[str, dict] = {}

    def _urlopen(self, url: str, timeout: int = 60):
        req = urllib.request.Request(url, headers={"User-Agent": self._ua, "Accept": "*/*"})
        return urllib.request.urlopen(req, timeout=timeout, context=self._ctx)

    def download_project(self, project_key: str, force: bool = False) -> str:
        """Download ORACC project ZIP if not cached. Returns path to ZIP."""
        if project_key not in ORACC_PROJECTS:
            raise ValueError(f"Unknown project: {project_key}. Known: {list(ORACC_PROJECTS.keys())}")
        zip_path, size_mb, desc = ORACC_PROJECTS[project_key]
        zip_path = zip_path.replace("//", "/")  # fix typo from project list
        url = ORACC_BASE + zip_path
        out_path = os.path.join(self.cache_dir, os.path.basename(zip_path))

        if os.path.exists(out_path) and not force:
            local_size = os.path.getsize(out_path)
            # Verify size matches server-reported size
            try:
                with self._urlopen(url, timeout=15) as r:
                    remote_size = int(r.headers.get("Content-Length", 0))
                if local_size == remote_size and local_size > 0:
                    log.info(f"[{project_key}] Cache hit: {out_path} ({local_size:,} bytes)")
                    return out_path
            except Exception as e:
                log.warning(f"[{project_key}] Size check failed ({e}); using local cache anyway")
                if local_size > 0:
                    return out_path

        log.info(f"[{project_key}] Downloading {url} (~{size_mb} MB)...")
        try:
            with self._urlopen(url, timeout=300) as r:
                total = int(r.headers.get("Content-Length", 0))
                got = 0
                t0 = time.time()
                with open(out_path + ".tmp", "wb") as f:
                    while True:
                        chunk = r.read(64 * 1024)
                        if not chunk:
                            break
                        f.write(chunk)
                        got += len(chunk)
                        if total:
                            pct = got * 100.0 / total
                            rate = got / max(0.1, time.time() - t0) / 1024
                            print(f"\r  {pct:5.1f}%  {got:,}/{total:,} bytes  {rate:.0f} KB/s",
                                  end="", flush=True)
                os.rename(out_path + ".tmp", out_path)
                print()
            log.info(f"[{project_key}] Saved: {out_path} ({os.path.getsize(out_path):,} bytes)")
            return out_path
        except urllib.error.URLError as e:
            log.error(f"[{project_key}] Download failed: {e}")
            if os.path.exists(out_path + ".tmp"):
                os.remove(out_path + ".tmp")
            raise

    def extract_zip(self, zip_path: str, subdir: Optional[str] = None) -> str:
        """Extract ORACC ZIP to cache dir. Returns path to extracted dir."""
        extract_dir = os.path.join(self.cache_dir, os.path.splitext(os.path.basename(zip_path))[0] + "_extracted")
        if not subdir:
            subdir = ""
        target = os.path.join(extract_dir, subdir) if subdir else extract_dir
        if os.path.exists(target) and os.listdir(target):
            log.info(f"Already extracted: {target}")
            return target
        os.makedirs(extract_dir, exist_ok=True)
        log.info(f"Extracting {zip_path} -> {extract_dir}...")
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(extract_dir)
        log.info(f"Extracted {len(os.listdir(extract_dir))} top-level entries")
        return target

    def parse_catalogue(self, project: str, extract_dir: str) -> Iterator[OraccText]:
        """Parse ORACC catalogue.json into OraccText records."""
        cat_path = os.path.join(extract_dir, project, "catalogue.json")
        if not os.path.exists(cat_path):
            # Try one level up
            cat_path = os.path.join(extract_dir, "catalogue.json")
        if not os.path.exists(cat_path):
            log.warning(f"[{project}] No catalogue.json at {cat_path}")
            return
        log.info(f"[{project}] Reading {cat_path}")
        with open(cat_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        members = data.get("members", {})
        for pid, m in members.items():
            period = m.get("period", "") or ""
            # Normalize period: handle "Old Akkadian; Ur III" etc
            period_norm = period.split(";")[0].strip()
            year_start = PERIOD_TO_YEAR.get(period_norm) or PERIOD_TO_YEAR.get(period)
            # Some catalogs have "date_of_origin" but we ignore for catalogue-only pass
            genre = m.get("genre", "") or ""
            cat = GENRE_TO_CATEGORY.get(genre, "OTHER")
            # pleiades_coord may be string "[lat,lon]"
            lat, lon = None, None
            pc = m.get("pleiades_coord", "")
            if pc and pc.startswith("["):
                try:
                    coords = json.loads(pc)
                    lat, lon = coords[1], coords[0]  # pleiades uses [lon, lat] in cdli files
                except (json.JSONDecodeError, IndexError, TypeError):
                    pass
            yield OraccText(
                p_number=pid,
                project=project,
                designation=m.get("designation", "") or "",
                museum_no=m.get("museum_no", "") or "",
                collection=m.get("collection", "") or "",
                provenience=m.get("provenience", "") or "",
                pleiades_id=m.get("pleiades_id", "") or "",
                lat=lat,
                lon=lon,
                period=period,
                period_year_start=year_start,
                language=m.get("language", "") or "",
                genre=genre,
                genre_category=cat,
                subgenre=m.get("subgenre", "") or "",
                supergenre=m.get("supergenre", "") or "",
                material=m.get("material", "") or "",
                object_type=m.get("object_type", "") or "",
                publication_date=str(m.get("publication_date", "") or ""),
                primary_publication=m.get("primary_publication", "") or "",
            )

    def merge_metadata(self, project: str, extract_dir: str, texts: dict[str, OraccText]):
        """Merge metadata.json's 'formats' field (atf/lem/tr-en) into texts dict in-place."""
        meta_path = os.path.join(extract_dir, project, "metadata.json")
        if not os.path.exists(meta_path):
            meta_path = os.path.join(extract_dir, "metadata.json")
        if not os.path.exists(meta_path):
            return
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        formats = meta.get("formats", {})
        for kind in ("atf", "lem", "xtf", "tr-en"):
            pids = formats.get(kind, [])
            attr = f"has_{kind.replace('-', '_')}"
            for pid in pids:
                if pid in texts:
                    setattr(texts[pid], attr, True)

    def enrich_pleiades(self, texts: dict[str, OraccText], rate_limit: float = 0.3):
        """Enrich texts with Pleiades coordinates via /places/{id}/json API.
        Caches per-Pleiades-ID to avoid re-fetching.
        """
        needed = set()
        for t in texts.values():
            if t.pleiades_id and (t.lat is None or t.lon is None):
                needed.add(t.pleiades_id)
        if not needed:
            log.info("All texts already have coordinates; skipping Pleiades enrichment")
            return
        log.info(f"Enriching {len(needed)} Pleiades place IDs...")
        for i, pid in enumerate(sorted(needed)):
            if pid in self._pleiades_cache:
                data = self._pleiades_cache[pid]
            else:
                try:
                    url = f"https://pleiades.stoa.org/places/{pid}/json"
                    with self._urlopen(url, timeout=15) as r:
                        data = json.loads(r.read())
                    self._pleiades_cache[pid] = data
                except Exception as e:
                    log.debug(f"Pleiades {pid} failed: {e}")
                    self._pleiades_cache[pid] = {}
                    continue
            rp = data.get("reprPoint") if isinstance(data, dict) else None
            if rp and len(rp) == 2:
                # Pleiades reprPoint is [lon, lat]
                lon, lat = rp[0], rp[1]
                for t in texts.values():
                    if t.pleiades_id == pid:
                        if t.lat is None:
                            t.lat = lat
                        if t.lon is None:
                            t.lon = lon
            if (i + 1) % 20 == 0:
                log.info(f"  Pleiades {i+1}/{len(needed)} done")
            time.sleep(rate_limit)
        # Save cache
        cache_path = os.path.join(self.output_dir, "pleiades_cache.json")
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(self._pleiades_cache, f, ensure_ascii=False)
        log.info(f"Pleiades cache saved: {cache_path}")

    def fetch_and_merge(
        self,
        project_keys: list[str],
        enrich_geo: bool = True,
        force_download: bool = False,
    ) -> list[OraccText]:
        """High-level: download + extract + parse multiple projects, return merged list."""
        all_texts: dict[str, OraccText] = {}
        for key in project_keys:
            try:
                zip_path = self.download_project(key, force=force_download)
                ext_dir = self.extract_zip(zip_path)
            except Exception as e:
                log.error(f"[{key}] Skipped due to error: {e}")
                continue
            # Determine the catalogue project subdir name
            # For ePSD2, files are at root or in 'epsd2/' etc. Try to find catalogue.json.
            for candidate in (key, key.split("-")[0], ""):
                try:
                    for t in self.parse_catalogue(candidate, ext_dir):
                        all_texts[t.p_number] = t
                    break
                except Exception as e:
                    log.debug(f"[{key}] parse as {candidate!r} failed: {e}")
            # Merge format availability
            for candidate in (key, key.split("-")[0], ""):
                try:
                    self.merge_metadata(candidate, ext_dir, all_texts)
                    break
                except Exception as e:
                    log.debug(f"[{key}] meta as {candidate!r} failed: {e}")
        if enrich_geo:
            self.enrich_pleiades(all_texts)
        return list(all_texts.values())

    def write_csv(self, texts: list[OraccText], path: str):
        """Write OraccText list to CSV (one row per text)."""
        if not texts:
            log.warning("No texts to write")
            return
        fieldnames = list(asdict(texts[0]).keys())
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for t in texts:
                row = asdict(t)
                # Convert Optional to string
                for k, v in row.items():
                    if v is None:
                        row[k] = ""
                w.writerow(row)
        log.info(f"Wrote {len(texts):,} rows to {path}")

    def write_json(self, texts: list[OraccText], path: str):
        """Write OraccText list to JSON."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump([asdict(t) for t in texts], f, ensure_ascii=False, indent=2)
        log.info(f"Wrote {len(texts):,} rows to {path}")

    def summarize(self, texts: list[OraccText]) -> dict:
        """Compute summary statistics for QA / reporting."""
        if not texts:
            return {"total": 0}
        period_count = Counter(t.period or "unknown" for t in texts)
        genre_count = Counter(t.genre_category for t in texts)
        lang_count = Counter(t.language or "unknown" for t in texts)
        proj_count = Counter(t.project for t in texts)
        has_period = sum(1 for t in texts if t.period)
        has_year = sum(1 for t in texts if t.period_year_start is not None)
        has_pleiades = sum(1 for t in texts if t.pleiades_id)
        has_geo = sum(1 for t in texts if t.lat is not None and t.lon is not None)
        with_atf = sum(1 for t in texts if t.has_atf)
        with_lem = sum(1 for t in texts if t.has_lem)
        with_tr = sum(1 for t in texts if t.has_tr_en)
        with_admin = sum(1 for t in texts if t.genre_category == "ADMIN")
        return {
            "total": len(texts),
            "by_project": dict(proj_count.most_common()),
            "top_periods": period_count.most_common(15),
            "top_genres": genre_count.most_common(15),
            "top_languages": lang_count.most_common(10),
            "data_quality": {
                "with_period": has_period,
                "with_year": has_year,
                "with_pleiades_id": has_pleiades,
                "with_coordinates": has_geo,
                "with_atf_transliteration": with_atf,
                "with_lemmatization": with_lem,
                "with_english_translation": with_tr,
                "admin_genre": with_admin,
            },
        }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="ORACC / ePSD2 fetcher for Civilization-Oracle")
    ap.add_argument(
        "--projects",
        nargs="+",
        default=["dcclt", "epsd2-ur3", "riao", "rinap", "etcsri"],
        help="ORACC project keys to fetch (see ORACC_PROJECTS dict)",
    )
    ap.add_argument("--output-dir", default=".", help="Output directory")
    ap.add_argument("--csv", default="oracc_catalog.csv", help="Output CSV filename")
    ap.add_argument("--json", default="oracc_catalog.json", help="Output JSON filename")
    ap.add_argument("--summary", default="oracc_summary.json", help="Summary JSON filename")
    ap.add_argument("--no-geo", action="store_true", help="Skip Pleiades enrichment")
    ap.add_argument("--force", action="store_true", help="Force re-download (overwrite cache)")
    ap.add_argument("--list", action="store_true", help="List available projects and exit")
    args = ap.parse_args()

    if args.list:
        print("Available ORACC projects:")
        for k, (path, size_mb, desc) in ORACC_PROJECTS.items():
            print(f"  {k:20s}  {size_mb:6.1f} MB  {desc}")
        print()
        print(f"Total: {sum(s[1] for s in ORACC_PROJECTS.values()):.1f} MB")
        return

    fetcher = OraccFetcher(output_dir=args.output_dir)
    texts = fetcher.fetch_and_merge(
        project_keys=args.projects,
        enrich_geo=not args.no_geo,
        force_download=args.force,
    )
    log.info(f"Total texts fetched: {len(texts):,}")

    csv_path = os.path.join(args.output_dir, args.csv)
    json_path = os.path.join(args.output_dir, args.json)
    summary_path = os.path.join(args.output_dir, args.summary)
    fetcher.write_csv(texts, csv_path)
    fetcher.write_json(texts, json_path)
    summary = fetcher.summarize(texts)
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    log.info(f"Summary: {summary}")
    log.info(f"Summary saved: {summary_path}")


if __name__ == "__main__":
    main()
