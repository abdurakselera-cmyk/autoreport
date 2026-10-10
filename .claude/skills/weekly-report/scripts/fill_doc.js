// Jalankan lewat mcp__playwright__browser_run_code_unsafe (parameter `filename`) dengan tab Google Doc journal
// terbuka (akun editor) dan server lokal aktif: python -m http.server 8765 --bind 127.0.0.1 (cwd = folder output).
// Ganti dua konstanta di bawah sesuai minggu yang dilaporkan. Lebar kolom diatur terpisah (SKILL.md langkah 6.6).
async (page) => {
  const WEEK = /Senin, 5 Oktober 2026 - Sabtu, 10 Oktober 2026/;            // judul periode (H3)
  const HTML = 'http://127.0.0.1:8765/Weekly-Report_2026-10-05_2026-10-10.html';

  const close = page.getByRole('button', { name: 'Tutup sheet samping' });
  if (await close.count()) { await close.first().click(); await page.waitForTimeout(500); }

  // 1. Hapus minggu yang sama kalau sudah ada (dari judul periode sampai akhir doc).
  const heading = page.getByRole('menuitem', { name: WEEK });
  if (await heading.count()) {
    await heading.first().click(); await page.waitForTimeout(1200);
    await page.keyboard.press('Home'); await page.keyboard.press('Control+Shift+End'); await page.waitForTimeout(600);
    await page.keyboard.press('Backspace'); await page.waitForTimeout(3000);
    if (await page.getByRole('menuitem', { name: WEEK }).count()) return 'gagal menghapus minggu lama';
  }

  // 2. Salin blok #paste sebagai rich text (viewport lebar agar tabel dirender 468pt) lalu tempel di akhir doc.
  const p2 = await page.context().newPage();
  await p2.setViewportSize({ width: 1400, height: 900 });
  await p2.goto(HTML);
  await p2.evaluate(() => {
    const r = document.createRange(); r.selectNode(document.getElementById('paste'));
    const s = getSelection(); s.removeAllRanges(); s.addRange(r);
  });
  await p2.keyboard.press('Control+c'); await p2.waitForTimeout(500); await p2.close();
  await page.bringToFront(); await page.locator('.kix-appview-editor').click();
  await page.keyboard.press('Control+End'); await page.waitForTimeout(500);
  await page.keyboard.press('Control+v'); await page.waitForTimeout(6000);

  // 3. Pilih seluruh tabel baru → Opsi tabel: matikan tinggi baris minimum, garis 1 poin.
  await page.getByRole('menuitem', { name: 'Abdur level 2' }).last().click(); await page.waitForTimeout(1200);
  await page.keyboard.press('Home'); await page.keyboard.press('Control+Shift+End'); await page.waitForTimeout(400);
  await page.keyboard.press('Shift+ArrowLeft'); await page.waitForTimeout(400);
  await page.getByRole('menuitem', { name: 'Format' }).click(); await page.waitForTimeout(500);
  await page.getByRole('menuitem', { name: /^Tabel/ }).hover(); await page.waitForTimeout(500);
  await page.getByRole('menuitem', { name: 'Opsi tabel' }).click(); await page.waitForTimeout(1200);
  const baris = page.getByRole('button', { name: 'Baris', exact: true });
  if ((await baris.getAttribute('aria-expanded')) !== 'true') { await baris.click(); await page.waitForTimeout(600); }
  const minH = page.getByRole('checkbox', { name: 'Ketinggian baris minimum' });
  if (await minH.isChecked()) { await minH.click(); await page.waitForTimeout(1500); }
  const warna = page.getByRole('button', { name: 'Warna', exact: true });
  if ((await warna.getAttribute('aria-expanded')) !== 'true') { await warna.click(); await page.waitForTimeout(600); }
  await page.getByRole('combobox', { name: 'Lebar batas tabel' }).click(); await page.waitForTimeout(500);
  await page.getByRole('option', { name: '1 poin', exact: true }).click(); await page.waitForTimeout(1000);
  return 'ok — lanjutkan atur lebar kolom (11,3 cm isi, 5,21 cm label) lalu verifikasi';
}
