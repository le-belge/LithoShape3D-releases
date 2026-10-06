#!/usr/bin/env python3
"""Garde-fou de publication : echoue si un dossier ou une archive a publier
contient du code source prive, un secret ou un depot Git.

Usage : check_publish_guard.py CHEMIN [CHEMIN ...]
  CHEMIN = dossier (bundle PyInstaller, .app) ou archive .zip.

Les regles visent la RACINE du bundle pour src/ et tests/ : les paquets
tiers (numpy, vtk...) embarquent legitimement leurs propres dossiers tests/.
Les fichiers .pem/.key sont refuses, sauf la liste blanche (certifi).
Aucune valeur de secret n'est jamais affichee : seulement le chemin et la regle.
"""
from __future__ import annotations

import fnmatch
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath

# Dossiers refuses a la racine du bundle (et sous Contents/Resources|MacOS|Frameworks,
# _internal pour PyInstaller >= 6).
ROOT_BASES = ("", "_internal", "Contents/Resources", "Contents/MacOS", "Contents/Frameworks")
FORBIDDEN_ROOT_DIRS = {"src", "tests", "licensing-server", "admin", "secrets"}

# Refuses n'importe ou dans l'arbre (composante exacte du chemin).
FORBIDDEN_ANY_COMPONENT = {".git", ".github", ".env", "id_rsa", "id_ed25519", "licensing-server", "secrets"}

# Motifs de nom de fichier refuses n'importe ou.
FORBIDDEN_FILE_GLOBS = ("*.pem", "*.key", ".env", ".env.*", "*private_key*", "*.p12", "*.pfx",
                        "issue_license*", "generate_license_keypair*")

# Faux positifs connus et legitimes (chemins finissant par...).
ALLOWED_SUFFIXES = ("certifi/cacert.pem", "certifi/py.typed")

# Fichiers .py du code prive : jamais en clair dans le bundle (PyInstaller les
# met dans l'archive PYZ). Un .py sous un dossier lithoshape3d/ = fuite.
PRIVATE_PY_RE = re.compile(r"(^|/)lithoshape3d/.*\.py$")

# Contenu : cle privee reelle (avec corps base64, pas le simple marqueur present
# dans libcrypto) et jetons GitHub.
SECRET_PATTERNS = [
    ("cle-privee-PEM", re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----\s*[A-Za-z0-9+/=\r\n]{60,}")),
    ("jeton-github", re.compile(rb"(github_pat_[A-Za-z0-9_]{30,}|gh[pousr]_[A-Za-z0-9]{30,})")),
    ("nom-secret-CI", re.compile(rb"SOURCE_REPO_TOKEN")),
]
# Bibliotheques natives : on ne scanne pas leur contenu (OpenSSL/GnuTLS/scipy
# contiennent des chaines qui ressemblent a des marqueurs de cle). Leur NOM
# reste verifie. Un secret ne se cache pas dans une .dll tierce.
BINARY_EXT = (".so", ".dylib", ".dll", ".pyd", ".a", ".lib")
CHUNK = 8 * 1024 * 1024
OVERLAP = 512
MAX_SCAN_FILE = 400 * 1024 * 1024


def check_name(rel: str) -> list[str]:
    problems = []
    # metadonnees AppleDouble (ditto --sequesterRsrc) : "._x" accompagne "x"
    rel = re.sub(r"(^|/)\._([^/]+)$", r"\1\2", rel)
    if rel.endswith(ALLOWED_SUFFIXES):
        return problems
    parts = PurePosixPath(rel).parts
    low = [p.lower() for p in parts]
    for comp in FORBIDDEN_ANY_COMPONENT:
        if comp in low:
            problems.append(f"composante interdite '{comp}'")
    posix = "/".join(parts)
    for base in ROOT_BASES:
        prefix = f"{base}/" if base else ""
        if posix.startswith(prefix):
            tail = posix[len(prefix):].split("/")
            if len(tail) > 1 and tail[0].lower() in FORBIDDEN_ROOT_DIRS:
                problems.append(f"dossier source/prive '{tail[0]}/' a la racine du bundle")
    name = parts[-1].lower() if parts else ""
    for g in FORBIDDEN_FILE_GLOBS:
        if fnmatch.fnmatch(name, g):
            problems.append(f"fichier interdit (motif {g})")
    if PRIVATE_PY_RE.search(posix):
        problems.append("source .py de lithoshape3d en clair")
    return problems


def scan_stream(fh, label: str) -> list[str]:
    hits, tail = [], b""
    while True:
        block = fh.read(CHUNK)
        if not block:
            break
        data = tail + block
        for rule, rx in SECRET_PATTERNS:
            if rx.search(data):
                hits.append(f"{label}: contenu suspect ({rule})")
        tail = data[-OVERLAP:]
    return sorted(set(hits))


def check_dir(root: Path) -> list[str]:
    errs = []
    for p in root.rglob("*"):
        rel = p.relative_to(root).as_posix()
        for pr in check_name(rel):
            errs.append(f"{root.name}/{rel}: {pr}")
        if p.is_file() and not p.is_symlink() and not rel.lower().endswith(BINARY_EXT) \
                and p.stat().st_size <= MAX_SCAN_FILE:
            with p.open("rb") as fh:
                errs += [f"{root.name}/{rel}: " + h.split(": ", 1)[1] for h in scan_stream(fh, rel)]
    return errs


def check_zip(path: Path) -> list[str]:
    errs = []
    with zipfile.ZipFile(path) as z:
        for info in z.infolist():
            rel = info.filename
            # les ZIP macOS ont un dossier racine unique (LithoShape3D.app/)
            top, _, rest = rel.partition("/")
            for pr in check_name(rest or rel) + (check_name(rel) if rest == "" else []):
                errs.append(f"{path.name}!{rel}: {pr}")
            if not info.is_dir() and not rel.lower().endswith(BINARY_EXT) \
                    and info.file_size <= MAX_SCAN_FILE:
                with z.open(info) as fh:
                    errs += [f"{path.name}!{rel}: " + h.split(": ", 1)[1] for h in scan_stream(fh, rel)]
    return errs


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    errors: list[str] = []
    for a in argv:
        p = Path(a)
        if not p.exists():
            errors.append(f"{a}: introuvable")
        elif p.is_dir():
            errors += check_dir(p)
        elif zipfile.is_zipfile(p):
            errors += check_zip(p)
        elif p.is_file():
            # installeur .exe : opaque, on ne verifie que le nom et le contenu brut
            errors += [f"{p.name}: " + h.split(": ", 1)[1] for h in scan_stream(p.open("rb"), p.name)]
            errors += [f"{p.name}: {x}" for x in check_name(p.name)]
    if errors:
        print("PUBLICATION BLOQUEE - elements interdits detectes :", file=sys.stderr)
        for e in errors[:100]:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print(f"OK garde-fou : {len(argv)} cible(s) propre(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
