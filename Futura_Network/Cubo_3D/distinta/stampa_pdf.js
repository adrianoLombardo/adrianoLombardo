// Converte distinta.html in PDF (A4 orizzontale). Uso: node stampa_pdf.js
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + path.join(__dirname, 'distinta.html'), { waitUntil: 'load' });
  await page.pdf({ path: path.join(__dirname, 'Cubo_Immersivo_distinta_Music_Box.pdf'),
                   format: 'A4', landscape: true, printBackground: true, preferCSSPageSize: true });
  await browser.close();
  console.log('PDF creato');
})();
