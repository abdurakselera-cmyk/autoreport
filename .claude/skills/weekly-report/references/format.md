# Format WORK WEEKLY JOURNAL – Abdur

Dipelajari dari minggu 14–19 Sep, 21–26 Sep, dan 28 Sep–3 Okt 2026. Selalu cek minggu terakhir di doc karena gaya
bisa bergeser.

## Struktur per minggu

```
<b>Senin, D Bulan YYYY - Sabtu, D Bulan YYYY</b>        ← paragraf tebal di atas tabel
┌──────────────────────────────────────────────┐
│                   Abdur (H2, colspan 2)      │
├───────────────┬──────────────────────────────┤
│ Pekerjaan     │ per hari (H4) → tugas bernomor│
│ Hasil pekerjaan│ 5 sorotan naratif            │
│ Progres       │ kategori A., B., … + Ringkasan│
│ Kendala       │ (biasanya kosong)            │
│ Solusi        │ (biasanya kosong)            │
│ Pertanyaan    │ (biasanya kosong)            │
└───────────────┴──────────────────────────────┘
```

Judul doc "WORK WEEKLY JOURNAL - ABDUR" hanya ada sekali di paling atas; jangan diulang.

## Pekerjaan
- Heading per hari: `Senin, 5 Oktober 2026` (nama hari + bulan Indonesia, tahun lengkap).
- Tugas bernomor mulai 1 tiap hari, judul tebal, contoh: `Pembuatan Konten Motion dengan Voice Over (Berbagai Brand)`.
- Sub-bullet berlabel: `Tujuan:`, `Detail Konten:` / `Detail Kunjungan:`, `Status:`, lalu link
  (`Link File:`, `Link Folder:`, `Link Adobe:`, `Daftar Link Hasil …:` dengan sub-bullet `Label: url`).
- Status memakai kalimat: `Selesai.`, `Selesai dan sudah di-acc oleh Kak …`, `Sedang dalam proses (On Process).`,
  `Selesai, menunggu …`.
- Sebut alat yang dipakai jika ada: Claude Luna, Claude Code, Creative Maker, CapCut, Adobe Lightroom.

## Hasil pekerjaan
- Tepat 5 sorotan, bernomor, judul tebal, dipisah garis `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`.
- Tiap sorotan 1 paragraf (3–5 kalimat) yang menggabungkan beberapa task lintas hari, menyebut hari & tanggal dalam
  kurung `(Senin, 5 Okt)` atau `Pada Rabu (7 Okt)`, angka total (jumlah video/konten/brand), dan status akhir
  (di-acc, siap tayang, menunggu review).
- Judul bergaya ringkas-berdampak: "Restock Masif 540 Video Motion untuk Lima Cabang", "Produksi 12 Konten …".

## Progres
- Kategori huruf `A.`, `B.`, … dengan jumlah task: `A. Produksi Stok Konten Motion – Creative Maker (2 task)`.
- Nomor task **berlanjut** lintas kategori (1…N), format `N. Judul – Detail (5 Okt)` atau rentang `(6–7 Okt)`.
- Di bawah tiap task: baris `Link …:`, `Detail:`, `Status: Selesai — …`, `Tujuan: …` (pakai em dash `—`).
- Kategori dipisah garis `━━━`.
- Kategori terakhir yang selesai selalu `Administrasi (1 task)` → `Penyusunan & Pengiriman Laporan Mingguan – Weekly
  Report (Sabtu)`, `Status: Selesai`.
- Task yang belum selesai dikumpulkan di bawah judul `DALAM PROSES (On Process)` dengan kategori sendiri.
- Penutup:
  ```
  Ringkasan
  Total Task: N
  Selesai: X task
  On Process: Y task (judul task on process)
  ```

## Skema `weekly.json` (input render_weekly.py)

```json
{
  "nama": "Abdur",
  "periode": {"mulai": "2026-10-05", "selesai": "2026-10-10"},
  "pekerjaan": [
    {"tanggal": "2026-10-05", "tasks": [
      {"judul": "…", "items": [
        {"label": "Tujuan", "text": "…"},
        {"label": "Status", "text": "Selesai."},
        {"label": "Daftar Link Hasil Revisi", "links": [{"label": "Judul konten", "url": "https://…"}]}
      ]}
    ]}
  ],
  "hasil": [{"judul": "…", "isi": "paragraf"}],
  "progres": [
    {"kategori": "…", "tasks": [
      {"judul": "…", "tanggal": "5 Okt", "items": [{"label": "Link File", "text": "https://…"}, {"label": "Tujuan", "text": "…"}]}
    ]},
    {"kategori": "…", "on_process": true, "tasks": [ … ]}
  ],
  "kendala": "", "solusi": "", "pertanyaan": ""
}
```

- Kategori dengan `"on_process": true` otomatis ditaruh di bawah "DALAM PROSES" dan dihitung sebagai On Process.
- `links[].url` boleh berisi teks biasa (mis. daftar topik tanpa link); renderer hanya menautkan string yang berupa URL.
