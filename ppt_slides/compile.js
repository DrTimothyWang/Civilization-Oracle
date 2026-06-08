const pptxgen = require('pptxgenjs');
const pres = new pptxgen();

pres.layout = 'LAYOUT_16x9';
pres.title = 'Civilization-Oracle v2.4';
pres.author = 'Wang Dianrang';
pres.subject = 'Civilization-Oracle Presentation';

// Vintage & Academic theme
const theme = {
  primary:   '003049',   // deep blue - main text
  secondary: '780000',   // deep red - accents
  accent:    'c1121f',   // bright red - highlights
  light:     '669bbc',   // light blue - secondary
  bg:        'fdf0d5'    // cream - backgrounds
};

// Load slides in order
require('./slide-01-cover.js').createSlide(pres, theme);
require('./slide-02-toc.js').createSlide(pres, theme);
require('./slide-03-background.js').createSlide(pres, theme);
require('./slide-04-architecture.js').createSlide(pres, theme);
require('./slide-05-bayesian.js').createSlide(pres, theme);
require('./slide-06-sikubert-ipw.js').createSlide(pres, theme);
require('./slide-07-four-dynasty.js').createSlide(pres, theme);
require('./slide-08-ipw-detail.js').createSlide(pres, theme);
require('./slide-09-findings.js').createSlide(pres, theme);
require('./slide-10-closing.js').createSlide(pres, theme);

pres.writeFile({ fileName: './output/Civilization-Oracle_v2.4_presentation.pptx' })
  .then(() => console.log('Done: Civilization-Oracle_v2.4_presentation.pptx'))
  .catch(e => { console.error(e); process.exit(1); });
