# Madad — NGO Operations Database (Pakistan)

A mobile-first, plain-language web app that shows **real humanitarian operations data**:
who is helping, where, and with what — built for flood-affected people ("Find Help")
and for NGOs/government coordinators ("Coordinator" dashboard with coverage gaps).

**Live data: none.** This is a clearly-labeled **snapshot** (see Data source card in the app).

## Real dataset used

- **Dataset:** "Pakistan: Who does What, Where, When and for Whom (5W)"
- **Publisher:** OCHA Pakistan, via the Humanitarian Data Exchange (HDX)
- **URL:** https://data.humdata.org/dataset/pakistan-who-does-what-where-when-and-for-whom-5w
- **License:** CC BY-IGO (Creative Commons Attribution for Intergovernmental Organisations)
- **Resource file:** `PAK_5W_24072025.xlsx` — **snapshot date 2026-07-24**, downloaded 2026-10-02
- **Raw rows:** 20,164 → normalized & deduped to **2,139 unique activity records**
  (dedupe key: organization + district + sector + activity; beneficiary counts summed,
  tehsils/descriptions merged). **All organizations, districts, sectors and activities are real —
  nothing is invented.**
- Coverage is dominated by the **Monsoon Floods 2025** response (18,248 of 20,164 raw rows),
  plus Education, Health-SRH, Nutrition, Protection-GBV, Food Security & Livelihood,
  WASH, Shelter/NFI and other sectors across Punjab, Sindh, Khyber Pakhtunkhwa,
  Balochistan, Gilgit-Baltistan and Azad Kashmir.

## How to refresh from HDX

1. Visit the dataset page (URL above) and download the newest `PAK_5W_*.xlsx` resource
   (no login needed; the download URL redirects to an S3 signed link — use `curl -L`).
2. Save it as `/tmp/ngo5w/pak_5w.xlsx` (any name works — update `SRC` in the script).
3. Run `python3 build_data.py` (needs `openpyxl`; no other deps).
4. Copy the regenerated `data/data.json` over the old one and redeploy.
5. Update the `snapshot_date` / `downloaded_date` in the script's `meta` block so the
   in-app "Data source" card and the snapshot badge stay honest.

## Structure

```
index.html        # the whole app (no build step, GitHub Pages ready)
data/data.json    # normalized real data + meta (generated, 806 KB)
build_data.py     # HDX XLSX → data.json pipeline (normalization rules live here)
README.md         # this file
```

## App features

- **Find Help tab:** district search (tolerant of spelling mistakes) + 6 big need
  buttons (Food, Shelter, Health, Water/WASH, Education, Protection) mapped from the
  real sector values → plain-language organization cards (org name, what they do,
  sector, area, people reached, working-now/finished status). Honest empty states —
  never invents contacts; points to PDMA helpline / district administration.
- **Coordinator tab:** province/sector/org/status/response filters, KPI cards,
  organizations-by-sector and top-districts bar charts (pure CSS, no CDN dependency),
  **coverage-gaps panel** computed from the data (districts with zero recorded actors
  per need + districts with only 1–2 organizations) with plain-language deployment
  recommendations, organization activity summary table, **CSV export** of filtered results.
- **Honesty:** visible data-source card (HDX title + URL, publisher, CC BY-IGO license,
  snapshot/download dates, row counts) and a "data snapshot — not live" badge.
  No fake LIVE indicators anywhere.

## QA (2026-10-02)

- JSON parses: `python3 -c "json.load(open('data/data.json'))"` OK (2,139 rows)
- JS syntax: `node --check` on extracted inline script — pass
- Served with `python3 -m http.server`, `curl` → HTTP 200 for `/` and `/data/data.json`
- Key markers present: `findResults`, `districtList`, `sectorBars`, `gaps`, `exportBtn`, `sourceCard`, `snapshotBadge`
- Total size: ~830 KB (well under 5 MB), phone-friendly, no build step.
