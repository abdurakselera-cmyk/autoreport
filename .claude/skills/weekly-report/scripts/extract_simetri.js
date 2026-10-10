// Jalankan lewat mcp__playwright__browser_evaluate di https://team.simetri.work/reports
// (setelah login). Mengembalikan semua kartu harian yang sedang tampil di halaman:
// [{ date: "Monday 5 October", plan: "...", report: "...", attachments: [{name, url}] }]
//
// Halaman ini dirender server (Next.js RSC), tidak ada API JSON, jadi teks diambil dari DOM.
// Pakai innerText (bukan snapshot) karena snapshot aksesibilitas memotong teks panjang.
() => {
  const DAY = /^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday) \d{1,2} \w+$/;
  const heads = [...document.querySelectorAll('p')].filter(p => DAY.test(p.textContent.trim()));
  return heads.map(p => {
    const card = p.parentElement;
    const text = card.innerText.replace(/ /g, ' ');
    // Kartu berisi blok "PLAN" lalu "REPORT" (label bisa diikuti "· edited once").
    const planMatch = text.match(/\bPLAN\b[^\n]*\n([\s\S]*?)(?=\n\s*REPORT\b|\n\s*No report was written|$)/i);
    const reportMatch = text.match(/\bREPORT\b[^\n]*\n([\s\S]*)$/i);
    return {
      date: p.textContent.trim(),
      plan: planMatch ? planMatch[1].trim() : '',
      report: reportMatch ? reportMatch[1].trim() : '',
      no_report: /No report was written/i.test(text),
      attachments: [...card.querySelectorAll('a')]
        .filter(a => a.href.includes('/api/reports/file/'))
        .map(a => ({ name: a.innerText.replace(/\s+/g, ' ').trim(), url: a.href })),
    };
  });
}
