function createSlide(pres, theme) {
 const slide = pres.addSlide();
 slide.background = { color: theme.bg };

 // Header bar
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 0, y: 0, w: 10, h: 0.55,
 fill: { color: theme.secondary }
 });
 slide.addText("CONTENTS", {
 x: 0.5, y: 0, w: 9, h: 0.55,
 fontSize: 13, fontFace: "Arial",
 color: theme.bg, bold: true,
 valign: "middle", margin: 0
 });

 // Section items - two column layout
 const sections = [
 { num: "01", title: "研究背景与核心问题", sub: "Background & RQs" },
 { num: "02", title: "系统架构概览", sub: "Architecture" },
 { num: "03", title: "PSI贝叶斯推断框架", sub: "Bayesian PSI" },
 { num: "04", title: "SikuBERT古籍NLP + IPW偏差校正", sub: "NLP & Bias Correction" },
 { num: "05", title: "四朝全周期PSI分析", sub: "Full-Period PSI" },
 { num: "06", title: "IPW校正详细效果", sub: "IPW Results" },
 { num: "07", title: "关键发现与学术贡献", sub: "Key Findings" },
 { num: "08", title: "下一步与致谢", sub: "Next Steps" }
 ];

 // Left column (01-04)
 sections.slice(0, 4).forEach((s, i) => {
 const y = 0.85 + i * 1.1;
 // Number circle
 slide.addShape(pres.shapes.OVAL, {
 x: 0.5, y: y, w: 0.45, h: 0.45,
 fill: { color: theme.secondary }
 });
 slide.addText(s.num, {
 x: 0.5, y: y, w: 0.45, h: 0.45,
 fontSize: 12, fontFace: "Arial",
 color: theme.bg, bold: true,
 align: "center", valign: "middle"
 });
 // Title
 slide.addText(s.title, {
 x: 1.1, y: y, w: 3.8, h: 0.3,
 fontSize: 15, fontFace: "Microsoft YaHei",
 color: theme.primary, bold: true, margin: 0
 });
 slide.addText(s.sub, {
 x: 1.1, y: y + 0.3, w: 3.8, h: 0.22,
 fontSize: 10, fontFace: "Arial",
 color: theme.light, margin: 0
 });
 });

 // Right column (05-08)
 sections.slice(4).forEach((s, i) => {
 const y = 0.85 + i * 1.1;
 slide.addShape(pres.shapes.OVAL, {
 x: 5.2, y: y, w: 0.45, h: 0.45,
 fill: { color: theme.accent }
 });
 slide.addText(s.num, {
 x: 5.2, y: y, w: 0.45, h: 0.45,
 fontSize: 12, fontFace: "Arial",
 color: theme.bg, bold: true,
 align: "center", valign: "middle"
 });
 slide.addText(s.title, {
 x: 5.8, y: y, w: 3.8, h: 0.3,
 fontSize: 15, fontFace: "Microsoft YaHei",
 color: theme.primary, bold: true, margin: 0
 });
 slide.addText(s.sub, {
 x: 5.8, y: y + 0.3, w: 3.8, h: 0.22,
 fontSize: 10, fontFace: "Arial",
 color: theme.light, margin: 0
 });
 });

 // Page number
 slide.addText("02", {
 x: 9.3, y: 5.1, w: 0.5, h: 0.35,
 fontSize: 10, fontFace: "Arial",
 color: theme.light, align: "right", valign: "middle"
 });
}
module.exports = { createSlide };
