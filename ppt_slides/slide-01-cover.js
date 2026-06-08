function createSlide(pres, theme) {
 const slide = pres.addSlide();
 slide.background = { color: theme.bg };

 // Left accent bar (deep red)
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 0, y: 0, w: 0.35, h: 5.625,
 fill: { color: theme.secondary },
 line: { color: theme.secondary }
 });

 // Top decorative line
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 0.35, y: 0.6, w: 2.5, h: 0.04,
 fill: { color: theme.accent }
 });

 // Main title
 slide.addText("Civilization-Oracle", {
 x: 0.6, y: 0.75, w: 8.5, h: 0.9,
 fontSize: 46, fontFace: "Georgia",
 color: theme.primary, bold: true, margin: 0
 });

 // Subtitle
 slide.addText("基于中华文明语义深度分析的历史预测系统", {
 x: 0.6, y: 1.65, w: 8.5, h: 0.5,
 fontSize: 22, fontFace: "Microsoft YaHei",
 color: theme.secondary, margin: 0
 });

 // Version badge
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 0.6, y: 2.35, w: 1.4, h: 0.38,
 fill: { color: theme.secondary },
 rectRadius: 0.05
 });
 slide.addText("v2.4", {
 x: 0.6, y: 2.35, w: 1.4, h: 0.38,
 fontSize: 14, fontFace: "Arial",
 color: theme.bg, bold: true,
 align: "center", valign: "middle"
 });

 // Divider
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 0.6, y: 3.0, w: 7, h: 0.02,
 fill: { color: theme.light }
 });

 // Author and info
 slide.addText("王滇让研究团队", {
 x: 0.6, y: 3.2, w: 8, h: 0.38,
 fontSize: 16, fontFace: "Microsoft YaHei",
 color: theme.primary, bold: true
 });
 slide.addText("广州中医药大学 公共卫生管理学院", {
 x: 0.6, y: 3.58, w: 8, h: 0.32,
 fontSize: 13, fontFace: "Microsoft YaHei",
 color: theme.light
 });
 slide.addText("学术顾问: 马利军 教授(语义心理学)", {
 x: 0.6, y: 3.9, w: 8, h: 0.32,
 fontSize: 13, fontFace: "Microsoft YaHei",
 color: theme.light
 });

 // Bottom right decoration
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 7.5, y: 4.8, w: 2.5, h: 0.04,
 fill: { color: theme.accent }
 });
 slide.addText("Digital Humanities", {
 x: 7.5, y: 4.9, w: 2.5, h: 0.3,
 fontSize: 11, fontFace: "Arial",
 color: theme.light, align: "right"
 });
}
module.exports = { createSlide };
