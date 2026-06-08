"""
CDLI Data Ingestor for Civilization-Oracle Cross-Civilizational Validation
Version: v1.0 (2026-05-31)
"""

import urllib.request
import json
import ssl
import time
from typing import Optional


class CDLIDataIngestor:
    """CDLI (Cuneiform Digital Library Initiative) data ingestion module.
    
    CDLI API Documentation: https://cdli.earth/docs/api
    Artifacts: https://cdli.earth/artifacts.json
    Inscriptions: https://cdli.earth/inscriptions.json
    """

    BASE_URL = "https://cdli.earth"

    def __init__(self):
        self._ctx = ssl.create_default_context()
        self._ctx.check_hostname = False
        self._ctx.verify_mode = ssl.CERT_NONE

    def _get(self, endpoint: str, params: Optional[dict] = None, timeout: int = 15) -> list:
        """Generic GET request to CDLI API."""
        url = f"{self.BASE_URL}/{endpoint}"
        if params:
            url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
        
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Civilization-Oracle/1.0 (Academic Research)',
            'Accept': 'application/json'
        })
        
        with urllib.request.urlopen(req, timeout=timeout, context=self._ctx) as resp:
            return json.loads(resp.read())

    def get_artifacts(self, limit: int = 100, offset: int = 0) -> list:
        """Fetch artifact list with pagination."""
        return self._get("artifacts.json", {"limit": limit, "offset": offset})

    def get_artifact(self, artifact_id: int) -> dict:
        """Fetch single artifact by ID."""
        return self._get(f"artifacts/{artifact_id}.json")

    def get_inscriptions(self, limit: int = 20, offset: int = 0) -> list:
        """Fetch inscription list with transliterations."""
        return self._get("inscriptions.json", {"limit": limit, "offset": offset})

    def get_inscription_by_artifact(self, artifact_id: int) -> Optional[dict]:
        """Fetch inscription for a specific artifact."""
        ins_list = self._get("inscriptions.json", {"artifact_id": artifact_id, "limit": 1})
        return ins_list[0] if ins_list else None

    def get_artifacts_by_period(self, period_name: str, max_results: int = 1000) -> list:
        """Search for artifacts by period name (e.g., 'Roman', 'Old Babylonian').
        
        Note: CDLI period field format is 'Period Name (ca. start-end CE/BCE)'
        Period names from CDLI: Uruk III, Early Dynastic, Old Akkadian, 
        Old Babylonian, Middle Babylonian, Neo-Assyrian, Neo-Babylonian,
        Persian, Hellenistic, Roman, etc.
        
        Returns list of artifact dicts matching the period.
        """
        all_artifacts = []
        offset = 0
        
        while len(all_artifacts) < max_results:
            batch = self.get_artifacts(limit=100, offset=offset)
            if not batch:
                break
            
            for artifact in batch:
                periods = artifact.get('period', [])
                for p in periods:
                    p_name = p if isinstance(p, str) else p.get('period', '')
                    if period_name.lower() in p_name.lower():
                        all_artifacts.append(artifact)
                        if len(all_artifacts) >= max_results:
                            return all_artifacts
            
            offset += 100
            time.sleep(0.3)  # Rate limiting
        
        return all_artifacts

    def get_roman_artifacts(self, max_results: int = 500) -> list:
        """Convenience method: get Roman period artifacts (ca. 0-640 CE).
        
        Roman period in CDLI = artifacts from Roman-ruled Mesopotamia
        (mainly Parthian and Sassanian periods under Roman influence).
        """
        return self.get_artifacts_by_period("Roman", max_results=max_results)

    def batch_get_inscriptions(self, artifact_ids: list) -> dict:
        """Batch fetch inscriptions for multiple artifact IDs.
        
        Returns dict mapping artifact_id -> inscription dict.
        """
        result = {}
        
        for aid in artifact_ids:
            ins = self.get_inscription_by_artifact(aid)
            if ins:
                result[aid] = ins
            time.sleep(0.2)  # Rate limiting
        
        return result

    @staticmethod
    def clean_atf(atf_text: str) -> str:
        """Clean ATF (Annotated Text Format) transliteration for translation.
        
        Removes: line numbers, column markers, editorial tags, 
        sign annotations (e.g., ~a, #), and structural markup.
        Keeps: transliterated words only.
        """
        import re
        
        # Remove column/line markers
        text = re.sub(r'@(obverse|reverse|top|bottom|left|right|column\s*\d+)', '', atf_text, flags=re.I)
        
        # Remove sign annotations like ~a# or ~b
        text = re.sub(r'~[a-z]+#?', '', text)
        
        # Remove parenthetical notes like (uncertain)
        text = re.sub(r'\([^)]*\)', '', text)
        
        # Remove editorial codes like >>A, >>>B
        text = re.sub(r'>>>?[A-Z]', '', text)
        
        # Remove numbers (word counts, etc) except as word separators
        text = re.sub(r'\s+\d+\s+', ' ', text)
        
        # Remove standalone single characters
        text = re.sub(r'\b[A-Z0-9]+\b(?:\s|$)', lambda m: m.group(0).strip() if len(m.group(0).strip()) > 2 else '', text)
        
        # Clean whitespace
        text = ' '.join(text.split())
        
        return text

    @staticmethod
    def extract_period_dates(period_str: str) -> tuple:
        """Extract start/end dates from CDLI period string.
        
        Input: 'Roman (ca. 0-640 CE)'
        Output: (0, 640) in CE years
        
        Returns (start_year, end_year) or (None, None) if parse fails.
        """
        import re
        
        # Match patterns like "ca. 0-640 CE" or "3000-2800 BC"
        pattern = r'ca?\.\s*(-?\d+)\s*[-–]\s*(-?\d+)\s*(CE|BCE|BC|AD)?'
        match = re.search(pattern, period_str, re.I)
        
        if match:
            start = int(match.group(1))
            end = int(match.group(2))
            era = match.group(3) or ''
            
            # Handle BCE: convert to negative years
            if 'BC' in era or 'BCE' in era:
                start = -start
                end = -end
            
            return (start, end)
        
        return (None, None)

    @staticmethod
    def map_to_century_windows(start: int, end: int) -> list:
        """Map a date range to century-level time windows.
        
        Input: (0, 640)  # Roman period
        Output: [(0, 100), (100, 200), (200, 300), (300, 400), 
                 (400, 500), (500, 600), (600, 640)]
        """
        windows = []
        current = ((start // 100) + 1) * 100  # Round up to next century
        
        while current <= end:
            windows.append((max(start, current - 100), min(end, current)))
            current += 100
        
        return windows


def demo():
    """Demo: fetch and display Roman period artifacts."""
    ingestor = CDLIDataIngestor()

    print("Fetching first batch of artifacts from CDLI...")
    # Just get first batch to verify API works, don't paginate
    artifacts = ingestor.get_artifacts(limit=50)

    print(f"Got {len(artifacts)} artifacts")
    print()

    # Show all unique periods found
    period_counts = {}
    for artifact in artifacts:
        periods = artifact.get('period', [])
        for p in periods:
            p_name = p if isinstance(p, str) else p.get('period', '')
            p_short = p_name.split('(')[0].strip()[:40] if p_name else 'unknown'
            period_counts[p_short] = period_counts.get(p_short, 0) + 1

    print(f"Unique periods in first 50 artifacts ({len(period_counts)} types):")
    for p, c in sorted(period_counts.items(), key=lambda x: -x[1]):
        print(f"  {c:2d} {p}")

    print()
    # Show sample inscription
    print("Sample inscription:")
    ins = ingestor.get_inscriptions(limit=3)
    if ins:
        item = ins[0]
        print(f"  Artifact ID: {item.get('artifact_id')}")
        trans = item.get('transliteration_clean', item.get('transliteration', ''))[:200]
        print(f"  Transliteration: {trans}")
        clean = ingestor.clean_atf(trans)
        print(f"  Cleaned ATF: {clean}")


if __name__ == '__main__':
    demo()