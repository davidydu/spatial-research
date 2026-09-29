#!/usr/bin/env bash
# Post-wave mechanical checks for D-26. Run from the vault root after every wave.
# Usage: d26_wave_check.sh [--skip-status]   (use --skip-status during Wave 0,
# when the main session legitimately has many uncommitted files; after the
# Wave 0 commit the status section is the audit of what subagents touched)
set -u
shopt -s nullglob
cd "$(dirname "$0")/../.."
fail=0
research=("20 - Research Notes/50 - Decision Records/D-26-research/"*.md)
mapping=("35 - Python Surface Mapping/"[1-9A-Z]*.md)
if [ "${1:-}" != "--skip-status" ]; then
  echo "== unexpected changes (expect none)"
  git status --porcelain | grep -vE '(D-26|d26|35 - Python Surface Mapping|progress-log|2026-09-25)' && fail=1
fi
echo "== schema (${#research[@]} research notes, ${#mapping[@]} mapping entries)"
if [ $(( ${#research[@]} + ${#mapping[@]} )) -gt 0 ]; then
  # ${arr[@]+"${arr[@]}"} is the bash-3.2-safe way to expand a possibly-empty array under set -u
  python3 "90 - Meta/scripts/validate_d26_note.py" ${research[@]+"${research[@]}"} ${mapping[@]+"${mapping[@]}"} || fail=1
fi
echo "== D-26.md frontmatter"
python3 - <<'EOF' || fail=1
import re,yaml,pathlib,sys
p=pathlib.Path("20 - Research Notes/50 - Decision Records/D-26.md")
if p.exists():
    fm=yaml.safe_load(re.match(r"\A---\n(.*?)\n---\n",p.read_text(),re.S).group(1))
    ok=fm.get("type")=="decision-record" and isinstance(fm.get("related-questions"),list) and all(isinstance(q,str) for q in fm["related-questions"])
    print("D-26.md frontmatter", "ok" if ok else "BAD (type or related-questions)"); sys.exit(0 if ok else 1)
EOF
echo "== duplicate stems (baseline 23)"
dups=$(find . -name '*.md' -not -path './.git/*' -exec basename {} .md \; | sort | uniq -d | wc -l | tr -d ' ')
echo "duplicates: $dups"; [ "$dups" -le 23 ] || fail=1
echo "== leak grep (expect nothing)"
grep -rnE 'accelerator-bandits|EE109-Spr-2026|/Users/david/|\.pem|ec2-[0-9]|us-west-2' "35 - Python Surface Mapping" "20 - Research Notes/50 - Decision Records/D-26"* 2>/dev/null && fail=1
echo "== citation density per research note (>= 8) and unverified count"
for f in ${research[@]+"${research[@]}"}; do
  c=$(grep -cE '@[0-9a-f]{7,}:|https?://' "$f"); u=$(grep -c 'inferred, unverified' "$f")
  printf '%3d cites %2d unverified  %s\n' "$c" "$u" "$f"; [ "$c" -ge 8 ] || fail=1
done
echo "== citation bounds"
python3 - <<'EOF' || fail=1
import re,subprocess,sys,pathlib
man=pathlib.Path("90 - Meta/reference-clones.md").read_text()
shas={r.split("|")[1].strip().split()[0]: r.split("|")[4].strip() for r in man.splitlines() if r.startswith("| ") and ("https://" in r or "local:" in r)}
LOCAL={"spatial-rs","spatial"}   # live under David_code/<name>, not reference/<name>
bad=0
for f in list(pathlib.Path("20 - Research Notes/50 - Decision Records").glob("D-26*/*.md"))+list(pathlib.Path("35 - Python Surface Mapping").glob("*.md")):
    for m in re.finditer(r"([a-z0-9-]+)@([0-9a-f]{7,}):([^\s:`]+):(\d+)-(\d+)", f.read_text()):
        name,sha,path,l1,l2=m.groups()
        root=pathlib.Path("/Users/david/Documents/David_code")/(name if name in LOCAL else f"reference/{name}")
        full=shas.get(name,""); target=root/path
        if not full.startswith(sha): print(f"{f}: {name}@{sha} not the manifest SHA"); bad+=1
        elif not target.is_file(): print(f"{f}: missing {target}"); bad+=1
        elif int(l2) > sum(1 for _ in open(target,errors="ignore")): print(f"{f}: {path}:{l1}-{l2} past EOF"); bad+=1
sys.exit(1 if bad else 0)
EOF
echo "== wikilinks in new notes resolve"
python3 - <<'EOF' || fail=1
import re,pathlib,sys
stems={p.stem for p in pathlib.Path(".").rglob("*.md") if ".git" not in p.parts}
paths={str(p.with_suffix("")) for p in pathlib.Path(".").rglob("*.md")}
bad=0
for f in list(pathlib.Path("20 - Research Notes/50 - Decision Records").glob("D-26*/*.md"))+list(pathlib.Path("35 - Python Surface Mapping").glob("*.md"))+[pathlib.Path("20 - Research Notes/50 - Decision Records/D-26.md")]:
    if not f.exists(): continue
    # Fenced source/transcripts can contain LUT literals such as [[1,2]].
    # Only prose outside those fences participates in Obsidian link resolution.
    prose=re.sub(r"(?ms)^```[^\n]*\n.*?^```[ \t]*$", "", f.read_text())
    for m in re.finditer(r"\[\[([^\]|#]+)", prose):
        t=m.group(1).strip()
        if t not in stems and t not in paths: print(f"{f}: unresolved [[{t}]]"); bad+=1
sys.exit(1 if bad else 0)
EOF
echo "== RESULT: $([ $fail -eq 0 ] && echo PASS || echo FAIL)"; exit $fail
