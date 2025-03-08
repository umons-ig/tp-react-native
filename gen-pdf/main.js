const puppeteer = require('puppeteer');

(async () => {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();

    // Liste des URLs à capturer en PDF
    const urls = [
        'https://tanguyvans.github.io/tp-react-native/',
        'https://tanguyvans.github.io/tp-react-native/docs/intro',
        'https://tanguyvans.github.io/tp-react-native/docs/prerequisites',
        'https://tanguyvans.github.io/tp-react-native/docs/exercices/create-project',
        'https://tanguyvans.github.io/tp-react-native/docs/exercices/hello-world',
        'https://tanguyvans.github.io/tp-react-native/docs/exercices/devnotes',
        'https://tanguyvans.github.io/tp-react-native/docs/exercices/devhub'
    ];

    const pdfs = [];

    for (const url of urls) {
        console.log(`📄 Génération du PDF pour : ${url}`);
        await page.goto(url, { waitUntil: 'networkidle0' });
        const pdf = await page.pdf({ format: 'A4', printBackground: true });
        pdfs.push(pdf);
    }

    await browser.close();

    // Fusionner les PDF en un seul fichier
    const { PDFDocument } = require('pdf-lib');
    const finalDoc = await PDFDocument.create();

    for (const pdfBytes of pdfs) {
        const pdfDoc = await PDFDocument.load(pdfBytes);
        const copiedPages = await finalDoc.copyPages(pdfDoc, pdfDoc.getPageIndices());
        copiedPages.forEach((page) => finalDoc.addPage(page));
    }

    const finalPdfBytes = await finalDoc.save();
    require('fs').writeFileSync('docs-complet.pdf', finalPdfBytes);

    console.log('✅ PDF global généré avec succès ! 📄');
})();
