function createSlide(pres, theme) {
 const slide = pres.addSlide();
 slide.background = { color: theme.bg };

 slide.addShape(pres.shapes.RECTANGLE, {
 x: 0, y: 0, w: 10, h: 0.55,
 fill: { color: theme.secondary }
 });
 slide.addText("02 系统架构概览", {
 x: 0.5, y: 0, w: 9, h: 0.55,
 fontSize: 14, fontFace: "Microsoft YaHei",
 color: theme.bg, bold: true,
 valign: "middle", margin: 0
 });

 // Pipeline stages
 const stages = [
 { label: "Stage 1", name: "数据采集", detail: "CBDB 658,339\n条人物记录", color: theme.light },
 { label: "Stage 2", name: "语义分析", detail: "SikuBERT\n双模式NLP", color: theme.secondary },
 { label: "Stage 3", name: "地理编码", detail: "CHGIS\nGSI计算", color: theme.light },
 { label: "Stage 4", name: "PSI计算", detail: "贝叶斯+IPW\n偏差校正", color: theme.secondary },
 { label: "Stage 5", name: "输出报告", detail: "四朝PSI\n因果链", color: theme.accent }
 ];

 stages.forEach((s, i) => {
 const x = 0.5 + i * 1.9;
 // Card
 slide.addShape(pres.shapes.RECTANGLE, {
 x: x, y: 0.85, w: 1.7, h: 2.1,
 fill: { color: s.color },
 rectRadius: 0.08
 });
 // Stage number
 slide.addText(s.label, {
 x: x, y: 0.95, w: 1.7, h: 0.3,
 fontSize: 9, fontFace: "Arial",
 color: s.color === theme.bg ? theme.secondary : theme.bg,
 align: "center", bold: true, margin: 0
 });
 // Stage name
 slide.addText(s.name, {
 x: x, y: 1.25, w: 1.7, h: 0.45,
 fontSize: 14, fontFace: "Microsoft YaHei",
 color: s.color === theme.bg ? theme.primary : theme.bg,
 bold: true, align: "center", valign: "middle", margin: 0
 });
 // Detail
 slide.addText(s.detail, {
 x: x, y: 1.75, w: 1.7, h: 1.0,
 fontSize: 10, fontFace: "Microsoft YaHei",
 color: s.color === theme.bg ? theme.primary : theme.bg,
 align: "center", valign: "middle", margin: 0
 });
 // Arrow
 if (i < stages.length - 1) {
 slide.addText(">", {
 x: x + 1.7, y: 1.65, w: 0.2, h: 0.5,
 fontSize: 20, fontFace: "Arial",
 color: theme.secondary, align: "center", valign: "middle"
 });
 }
 });

 // Bottom three feature cards
 const features = [
 { title: "贝叶斯层次推断", items: ["Bootstrap 2000次重抽样", "Jeffreys无信息先验", "SFD权重0.50", "Hedges' g小样本修正"] },
 { title: "SikuBERT双模式", items: ["ernie-3.0-mini-zh真实模型", "规则词典降级兜底", "20个高频概念词典", "情感方向验证正确"] },
 { title: "CBDB IPW偏差校正", items: ["倾向分模型(sigmoid)", "逆稳定化权重", "PSI 0.614->0.604", "高偏差样本正确降权"] }
 ];
 features.forEach((f, i) => {
 const x = 0.5 + i * 3.1;
 slide.addShape(pres.shapes.RECTANGLE, {
 x: x, y: 3.2, w: 2.9, h: 2.0,
 fill: { color: theme.light, transparency: 50 },
 rectRadius: 0.06
 });
 slide.addText(f.title, {
 x: x + 0.15, y: 3.3, w: 2.6, h: 0.35,
 fontSize: 12, fontFace: "Microsoft YaHei",
 color: theme.secondary, bold: true, margin: 0
 });
 f.items.forEach((item, j) => {
 slide.addText(" " + item, {
 x: x + 0.15, y: 3.68 + j * 0.35, w: 2.6, h: 0.3,
 fontSize: 10, fontFace: "Microsoft YaHei",
 color: theme.primary, margin: 0
 });
 });
 });

 // Page number
 slide.addText("04", {
 x: 9.3, y: 5.1, w: 0.5, h: 0.35,
 fontSize: 10, fontFace: "Arial",
 color: theme.light, align: "right", valign: "middle"
 });
}
module.exports = { createSlide };
