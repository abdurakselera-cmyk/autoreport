---
name: weekly-report
description: Menyusun WORK WEEKLY JOURNAL mingguan Abdur (periode Senin–Sabtu) dari laporan harian di team.simetri.work/reports, lalu mengisinya langsung ke Google Doc "WORK WEEKLY JOURNAL (Abdur) II" di bawah minggu terakhir. Pakai saat user minta "buat weekly report", "laporan mingguan", "isi weekly journal", atau menyebut periode Senin–Sabtu untuk dilaporkan.
---

# Weekly Report (WORK WEEKLY JOURNAL – Abdur)

Laporan dikirim **Sabtu sore**, periode **Senin–Sabtu minggu berjalan**. Hasil akhir **diisi langsung ke Google Doc
journal yang sama** (tambahkan minggu baru di bagian paling bawah). Jangan membuat dokumen lain sebagai hasil akhir
kecuali user memintanya.

## Konfigurasi lokal

Baca `config.local.json` di root project (tidak di-commit karena repo publik). Kalau belum ada, salin dari
`config.example.json` dan isi:

- `journal_doc_id` — ID Google Doc journal. Kalau tidak tahu: file `.gdoc` di Google Drive for Desktop tidak bisa dibaca
  langsung; cari ID-nya di `%LOCALAPPDATA%/Google/DriveFS/<akun>/metadata_sqlite_db` (salin dulu ke scratchpad, query
  tabel `items` dengan `local_title LIKE '%WEEKLY JOURNAL%'`, kolom `id`).
- `reports_url` — `https://team.simetri.work/reports`
- `drive_report_dir` — folder laporan harian lokal (`G:/Shared drives/Akselera Edtech/REPORT ABDUR`), berisi subfolder
  `YYYY-MM-DD/` dengan laporan Creative Maker / LunaEngine (`.md`).
- `output_dir` — tempat JSON/HTML kerja (default `output/`, di-gitignore).

## Langkah

### 1. Tentukan periode
Senin–Sabtu minggu ini (hari ini biasanya Sabtu). Cek dengan kalender sungguhan; kalau user menyebut tanggal yang
tidak cocok dengan harinya (mis. "Senin 3 Oktober" padahal 3 Okt itu Sabtu), pakai minggu yang dimaksud dan
sebutkan koreksinya di jawaban. Pastikan periode ini **belum ada** di journal (minggu terakhir di doc harus Sabtu
sebelumnya).

### 2. Pelajari format terbaru dari journal
Ekspor doc (`https://docs.google.com/document/d/<ID>/export?format=txt`, bisa juga `format=html` untuk struktur tabel)
dan baca **minggu terakhir** untuk gaya penulisan, kategori yang biasa dipakai, dan nama orang/tim. Aturan lengkapnya ada
di `references/format.md` — ikuti itu.

### 3. Ambil laporan harian dari Simetri (sumber utama)
Pakai Playwright MCP:
1. `browser_navigate` ke `reports_url`. Kalau diarahkan ke `/auth/login`, klik **Sign in with Google** lalu **minta user
   login sendiri** di jendela browser. Jangan pernah mengetik kredensial. Tunggu dengan `browser_wait_for` sampai URL
   kembali ke team.simetri.work.
2. Jalankan isi `scripts/extract_simetri.js` lewat `browser_evaluate` (simpan ke file di `output_dir`). Hasilnya per hari:
   `plan`, `report`, `no_report`, `attachments`.
3. Snapshot aksesibilitas memotong teks panjang, jadi selalu pakai hasil `innerText` dari script.

Catatan data:
- **Report** = pekerjaan yang benar-benar selesai/dikerjakan. **Plan** hanya dipakai untuk memperjelas detail
  (mis. rincian revisi). Item plan yang tidak muncul di report jangan dilaporkan sebagai selesai; sebutkan ke user.
- Link Drive bisa terpotong di Simetri (batas karakter). Pulihkan ID lengkapnya dari `metadata_sqlite_db` DriveFS
  (`items.id LIKE '<prefix>%'`). Jangan menebak.
- Perbaiki typo nama brand (mis. "Edusmo" → "Eduosmo", "Kramak" → "Krama").

### 4. Lengkapi hari yang belum ada report-nya
Sabtu sore biasanya baru ada Plan. Ambil pekerjaan hari itu dari `drive_report_dir/<YYYY-MM-DD>/` (subfolder
`LunaEngine/` dan file `Laporan-Harian-Creative-Maker_*.md`): baca frontmatter `judul`/`ringkas` dan bagian
"Perlu diputuskan". Status DRAF / menunggu keputusan = **On Process**. Laporan Drive dari hari lain yang tidak ada di
Simetri jangan dimasukkan diam-diam; tanyakan atau sebutkan ke user.

Selalu tambahkan task terakhir di hari Sabtu: **Penyusunan & Pengiriman Weekly Report Pekerjaan** (kategori
Administrasi, Selesai).

### 5. Susun JSON lalu render
Tulis `output_dir/<mulai>_<selesai>/weekly.json` sesuai skema di `references/format.md`, lalu:

```
python -I .claude/skills/weekly-report/scripts/render_weekly.py <weekly.json> <folder-output>
```

Hasil: `Weekly-Report_<mulai>_<selesai>.html` (blok `#paste` = judul periode + tabel) dan `.md` untuk dicek.
Ringkasan (Total/Selesai/On Process) dihitung otomatis dari kategori `progres`.

### 6. Isi ke Google Doc journal
Doc harus dibuka oleh akun yang punya **akses edit** (kalau muncul tombol "Minta akses edit", berhenti dan minta user
login dengan akun pemilik/editor atau memberi akses edit; jangan klik "Minta akses").

1. `browser_navigate` ke `https://docs.google.com/document/d/<ID>/edit`.
2. Buka HTML hasil render di tab baru (`file:///...html`), salin blok `#paste` sebagai rich text:
   `browser_evaluate` → `const r=document.createRange(); r.selectNode(document.getElementById('paste')); getSelection().removeAllRanges(); getSelection().addRange(r); document.execCommand('copy')`.
3. Kembali ke tab doc, klik area dokumen, tekan `Control+End` (ke paling bawah, di luar tabel minggu terakhir), tekan
   `Enter` dua kali, lalu `Control+V`.
4. Verifikasi: ekspor ulang `format=txt` dan pastikan heading periode baru + baris "Ringkasan" muncul tepat sekali di
   akhir doc dan minggu-minggu sebelumnya tidak berubah. Ambil screenshot bagian akhir untuk dicek user.

### 7. Laporkan ke user
Sebutkan: periode, jumlah task (selesai/on process), sumber yang dipakai untuk hari tanpa report, item plan yang tidak
dilaporkan, link yang dipulihkan, dan link doc. Jangan commit file di `output/` (berisi link internal).
