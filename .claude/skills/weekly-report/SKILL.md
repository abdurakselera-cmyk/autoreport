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
Kalau user menempelkan laporan harian (biasanya Sabtu) di chat, itu **sumber utama** untuk hari tersebut — pakai
status dan catatan pengiriman (ke Kak Bowo/Kak Zidan, dll.) persis seperti tertulis. Kalau tidak ada:
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
Doc harus dibuka oleh akun yang punya **akses edit**. Cek: tidak ada label "Minta akses edit" dan menubar punya
"Sisipkan"/"Format". Kalau masih view-only, berhenti dan minta user memberi akses Editor (akun Abdur:
abdur.akselera@gmail.com) atau login dengan akun editor; jangan klik "Minta akses".

Prosedur yang sudah terbukti jalan (10 Okt 2026). Semua langkah browser bisa digabung dalam satu
`browser_run_code_unsafe` (lihat `scripts/fill_doc.js`, ganti konstanta di atasnya):
1. Simpan pembanding: ekspor `format=txt` ke scratchpad (`before.txt`).
2. Playwright memblokir `file://`, jadi sajikan folder output lewat server lokal (background):
   `python -m http.server 8765 --bind 127.0.0.1` (cwd = folder output minggu itu).
3. Kalau minggu yang sama sudah ada di doc (mis. perlu diperbaiki), hapus dulu: klik judul periodenya di outline,
   `Home`, `Control+Shift+End`, `Backspace`. Pastikan export txt kembali sama persis dengan sebelum diisi.
4. Buka halaman HTML di tab baru dengan viewport lebar (≥1400px, agar tabel dirender pas 468pt), pilih blok `#paste`
   (Range + Selection), tekan tombol sungguhan `Control+c`, tutup tab.
5. Di tab doc: klik `.kix-appview-editor`, `Control+End`, `Control+V`. Tunggu "Disimpan ke Drive".
6. **Wajib dirapikan setelah tempel** (Docs mengubah dua hal ini saat menempel):
   - Pilih seluruh tabel baru: klik "Abdur" (outline, `.last()`), `Home`, `Control+Shift+End`, `Shift+ArrowLeft` →
     Format → Tabel → **Opsi tabel** → **Baris**: matikan "Ketinggian baris minimum" (kalau tidak, baris Pekerjaan
     terlempar ke halaman baru dan menyisakan ruang kosong); **Warna**: Batas tabel hitam, **1 poin**.
   - **Kolom**: kursor di kolom isi (klik hari terakhir di outline) = **11,3 cm**; lalu klik sel kolom label
     (`page.mouse.click` di area kolom kiri) = **5,21 cm**. Tutup panel.
7. Verifikasi: ekspor ulang `format=txt` + `format=html`. Syarat: teks lama adalah prefiks utuh dari teks baru,
   judul periode muncul sekali, "Total Task: N" cocok, tabel terakhir ≈ 147,8pt/320,2pt, garis 1pt `#000000`, semua
   tinggi baris 0pt. Ambil screenshot atas tabel, Hasil pekerjaan, dan Progres, bandingkan dengan minggu sebelumnya.
   Matikan server lokal setelah selesai.

### 7. Laporkan ke user
Sebutkan: periode, jumlah task (selesai/on process), sumber yang dipakai untuk hari tanpa report, item plan yang tidak
dilaporkan, link yang dipulihkan, dan link doc. Jangan commit file di `output/` (berisi link internal).
