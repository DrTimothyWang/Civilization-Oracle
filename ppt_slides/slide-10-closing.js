function createSlide(pres, theme) {
 const slide = pres.addSlide();
 slide.background = { color: theme.secondary };

 // Left accent
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 0, y: 0, w: 0.3, h: 5.625,
 fill: { color: theme.accent }
 });

 // Title
 slide.addText("NEXT STEPS", {
 x: 0.6, y: 0.5, w: 4, h: 0.35,
 fontSize: 11, fontFace: "Arial",
 color: theme.light, bold: true, margin: 0
 });
 slide.addText("下一步", {
 x: 0.6, y: 0.85, w: 5, h: 0.55,
 fontSize: 28, fontFace: "Microsoft YaHei",
 color: theme.bg, bold: true, margin: 0
 });

 // Next steps
 const steps = [
 { num: "1", title: "论文内部Review", detail: "提交马利军教授评审, 整合反馈意见" },
 { num: "2", title: "激活SikuBERT真实模型", detail: "pip install transformers, 接入ernie-3.0-mini-zh" },
 { num: "3", title: "CBDB真实专家数据", detail: "替换模拟数据, 3589条北宋专家记录" },
 { num: "4", title: "投稿Digital Humanities", detail: "目标期刊, 差异化定位语义深度分析" }
 ];

 steps.forEach((s, i) => {
 const y = 1.65 + i * 0.8;
 slide.addShape(pres.shapes.OVAL, {
 x: 0.6, y: y, w: 0.38, h: 0.38,
 fill: { color: theme.accent }
 });
 slide.addText(s.num, {
 x: 0.6, y: y, w: 0.38, h: 0.38,
 fontSize: 12, fontFace: "Arial",
 color: theme.bg, bold: true, align: "center", valign: "middle"
 });
 slide.addText(s.title, {
 x: 1.1, y: y - 0.02, w: 4, h: 0.28,
 fontSize: 13, fontFace: "Microsoft YaHei",
 color: theme.bg, bold: true, margin: 0
 });
 slide.addText(s.detail, {
 x: 1.1, y: y + 0.26, w: 4, h: 0.25,
 fontSize: 10, fontFace: "Microsoft YaHei",
 color: theme.light, margin: 0
 });
 });

 // Right: Thank you
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 5.5, y: 0, w: 4.5, h: 5.625,
 fill: { color: theme.primary }
 });
 slide.addText("THANK YOU", {
 x: 5.8, y: 0.8, w: 3.9, h: 0.6,
 fontSize: 32, fontFace: "Georgia",
 color: theme.bg, bold: true, margin: 0
 });
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 5.8, y: 1.5, w: 1.5, h: 0.04,
 fill: { color: theme.accent }
 });

 slide.addText("王滇让研究团队", {
 x: 5.8, y: 1.75, w: 3.9, h: 0.35,
 fontSize: 14, fontFace: "Microsoft YaHei",
 color: theme.bg, bold: true, margin: 0
 });
 slide.addText("广州中医药大学\n公共卫生管理学院", {
 x: 5.8, y: 2.15, w: 3.9, h: 0.55,
 fontSize: 12, fontFace: "Microsoft YaHei",
 color: theme.light, margin: 0
 });
 slide.addText("学术顾问: 马利军 教授", {
 x: 5.8, y: 2.75, w: 3.9, h: 0.3,
 fontSize: 11, fontFace: "Microsoft YaHei",
 color: theme.light, margin: 0
 });

 // Version badge
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 5.8, y: 3.3, w: 1.5, h: 0.38,
 fill: { color: theme.accent },
 rectRadius: 0.05
 });
 slide.addText("v2.4", {
 x: 5.8, y: 3.3, w: 1.5, h: 0.38,
 fontSize: 14, fontFace: "Arial",
 color: theme.bg, bold: true, align: "center", valign: "middle"
 });

 // Three highlights
 const highlights = [
 "贝叶斯PSI",
 "IPW偏差校正",
 "四朝全周期"
 ];
 highlights.forEach((h, i) => {
 const y = 3.95 + i * 0.42;
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 5.8, y: y, w: 0.06, h: 0.28,
 fill: { color: theme.accent }
 });
 slide.addText(h, {
 x: 6.0, y: y, w: 3.7, h: 0.28,
 fontSize: 12, fontFace: "Microsoft YaHei",
 color: theme.bg, margin: 0
 });
 });

 // Page number
 slide.addText("10", {
 x: 9.3, y: 5.1, w: 0.5, h: 0.35,
 fontSize: 10, fontFace: "Arial",
 color: theme.light, align: "right", valign: "middle"
 });
}
module.exports = { createSlide };
