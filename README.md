# Auto Report

Skill Claude Code untuk membuat **WORK WEEKLY JOURNAL** mingguan (Senin–Sabtu) dari laporan harian di
Simetri Team, lalu mengisinya langsung ke Google Doc journal.

## Isi

```
.claude/skills/weekly-report/
├── SKILL.md                  # alur kerja lengkap untuk Claude
├── references/format.md      # aturan format journal + skema weekly.json
└── scripts/
    ├── extract_simetri.js    # dijalankan via Playwright browser_evaluate di /reports
    └── render_weekly.py      # weekly.json -> HTML (untuk ditempel ke Google Doc) + Markdown
config.example.json           # salin ke config.local.json lalu isi
```

## Pemakaian

1. Salin `config.example.json` → `config.local.json`, isi `journal_doc_id`.
2. Buka Claude Code di folder ini (dengan Playwright MCP aktif), lalu minta:
   > buat weekly report minggu ini
3. Login sendiri ke Simetri / Google di jendela browser saat diminta. Claude tidak menyimpan kredensial.

`output/` dan `config.local.json` tidak di-commit karena repo ini publik.
