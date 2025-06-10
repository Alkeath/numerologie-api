const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
  const browser = await puppeteer.launch({ args: ['--no-sandbox'] });
  const page = await browser.newPage();

  // 🔁 Chemin relatif depuis le conteneur Docker
  const filePath = path.join(__dirname, '../../app/templates/template_temporaire1/index.html');
  const fileUrl = 'file://' + filePath;

  await page.goto(fileUrl, { waitUntil: 'networkidle0' });

  await page.pdf({
    path: 'rapport_test.pdf',
    format: 'A4',
    printBackground: true
  });

  await browser.close();
})();
