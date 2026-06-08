function createSlide(pres, theme) {
 const slide = pres.addSlide();
 slide.background = { color: theme.bg };

 slide.addShape(pres.shapes.RECTANGLE, {
 x: 0, y: 0, w: 10, h: 0.55,
 fill: { color: theme.secondary }
 });
 slide.addText("05 四朝全周期PSI分析", {
 x: 0.5, y: 0, w: 9, h: 0.55,
 fontSize: 14, fontFace: "Microsoft YaHei",
 color: theme.bg, bold: true,
 valign: "middle", margin: 0
 });

 // Bar chart using shapes
 const data = [
 { name: "Tang", period: "618-907", n: 50, psi: 0.327, gsi: 1.733 },
 { name: "NorthSong", period: "960-1127", n: 50, psi: 0.310, gsi: 1.683 },
 { name: "SouthSong", period: "1127-1279", n: 40, psi: 0.295, gsi: 1.755 },
 { name: "Ming", period: "1368-1644", n: 50, psi: 0.246, gsi: 1.683 }
 ];

 // Y-axis label
 slide.addText("PSI", {
 x: 0.2, y: 2.3, w: 0.3, h: 0.3,
 fontSize: 9, fontFace: "Arial",
 color: theme.light, margin: 0
 });

 // Grid lines
 [0, 0.1, 0.2, 0.3, 0.4].forEach((v, i) => {
 const y = 4.4 - v * 6;
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 0.8, y: y, w: 6.2, h: 0.01,
 fill: { color: theme.light, transparency: 70 }
 });
 slide.addText(v.toFixed(1), {
 x: 0.3, y: y - 0.1, w: 0.45, h: 0.22,
 fontSize: 8, fontFace: "Arial",
 color: theme.light, align: "right", margin: 0
 });
 });

 // Bars
 const barGroupW = 1.3;
 const barW = 0.5;
 const baseY = 4.4;
 const maxPsi = 0.4;
 const scale = 6.0;

 data.forEach((d, i) => {
 const gx = 1.0 + i * barGroupW;
 const barH = d.psi * scale;
 const y = baseY - barH;

 // Bar
 slide.addShape(pres.shapes.RECTANGLE, {
 x: gx, y: y, w: barW, h: barH,
 fill: { color: theme.accent }
 });
 // Value on bar
 slide.addText(d.psi.toFixed(3), {
 x: gx - 0.1, y: y - 0.25, w: barW + 0.2, h: 0.22,
 fontSize: 9, fontFace: "Arial",
 color: theme.accent, align: "center", bold: true, margin: 0
 });
 // Dynasty name
 slide.addText(d.name === "Tang" ? "Tang" : d.name === "NorthSong" ? "N.Song" : d.name === "SouthSong" ? "S.Song" : "Ming", {
 x: gx - 0.1, y: 4.45, w: barW + 0.2, h: 0.22,
 fontSize: 9, fontFace: "Arial",
 color: theme.primary, align: "center", bold: true, margin: 0
 });
 slide.addText(d.period, {
 x: gx - 0.2, y: 4.67, w: barW + 0.4, h: 0.2,
 fontSize: 8, fontFace: "Arial",
 color: theme.light, align: "center", margin: 0
 });
 });

 // Annotation
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 0.8, y: 4.9, w: 6.2, h: 0.01,
 fill: { color: theme.light }
 });

 // Right: Data table
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 7.5, y: 0.75, w: 2.2, h: 4.45,
 fill: { color: theme.light },
 rectRadius: 0.06
 });
 slide.addText("PSI校正值", {
 x: 7.6, y: 0.85, w: 2.0, h: 0.28,
 fontSize: 11, fontFace: "Microsoft YaHei",
 color: theme.secondary, bold: true, margin: 0
 });
 data.forEach((d, i) => {
 const y = 1.2 + i * 0.7;
 slide.addText(d.name === "Tang" ? "Tang" : d.name === "NorthSong" ? "N.Song" : d.name === "SouthSong" ? "S.Song" : "Ming", {
 x: 7.6, y: y, w: 2.0, h: 0.25,
 fontSize: 10, fontFace: "Arial",
 color: theme.secondary, bold: true, margin: 0
 });
 slide.addText(d.psi.toFixed(3), {
 x: 7.6, y: y + 0.22, w: 1.0, h: 0.22,
 fontSize: 13, fontFace: "Arial",
 color: theme.accent, bold: true, margin: 0
 });
 slide.addText("GSI " + d.gsi.toFixed(3), {
 x: 8.6, y: y + 0.22, w: 1.0, h: 0.22,
 fontSize: 10, fontFace: "Arial",
 color: theme.primary, margin: 0
 });
 slide.addText(d.n + " experts", {
 x: 7.6, y: y + 0.42, w: 2.0, h: 0.2,
 fontSize: 9, fontFace: "Arial",
 color: theme.light, margin: 0
 });
 if (i < 3) {
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 7.6, y: y + 0.64, w: 2.0, h: 0.01,
 fill: { color: theme.light, transparency: 60 }
 });
 }
 });

 // Insight box
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 7.5, y: 4.1, w: 2.2, h: 1.0,
 fill: { color: theme.secondary },
 rectRadius: 0.06
 });
 slide.addText("ALL CRISIS", {
 x: 7.6, y: 4.2, w: 2.0, h: 0.35,
 fontSize: 12, fontFace: "Arial",
 color: theme.accent, bold: true, margin: 0
 });
 slide.addText("四朝一致落在\n危机区间", {
 x: 7.6, y: 4.52, w: 2.0, h: 0.5,
 fontSize: 10, fontFace: "Microsoft YaHei",
 color: theme.bg, margin: 0
 });

 // Page number
 slide.addText("07", {
 x: 9.3, y: 5.1, w: 0.5, h: 0.35,
 fontSize: 10, fontFace: "Arial",
 color: theme.light, align: "right", valign: "middle"
 });
}
module.exports = { createSlide };
