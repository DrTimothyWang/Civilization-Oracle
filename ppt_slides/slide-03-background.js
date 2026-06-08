function createSlide(pres, theme) {
 const slide = pres.addSlide();
 slide.background = { color: theme.bg };

 // Header
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 0, y: 0, w: 10, h: 0.55,
 fill: { color: theme.secondary }
 });
 slide.addText("01 研究背景与核心问题", {
 x: 0.5, y: 0, w: 9, h: 0.55,
 fontSize: 14, fontFace: "Microsoft YaHei",
 color: theme.bg, bold: true,
 valign: "middle", margin: 0
 });

 // Left panel - background
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 0.4, y: 0.75, w: 4.5, h: 4.3,
 fill: { color: theme.light },
 rectRadius: 0.08
 });
 slide.addText("历史预测的两难", {
 x: 0.6, y: 0.9, w: 4.1, h: 0.35,
 fontSize: 14, fontFace: "Microsoft YaHei",
 color: theme.secondary, bold: true, margin: 0
 });
 slide.addText([
 { text: "Cliodynamics(Turchin)", options: { bold: true, breakLine: true } },
 { text: "Seshat全球历史数据库, 定量研究历史周期", options: { breakLine: true } },
 { text: "核心变量: 人口, 能量, 技术", options: { breakLine: true } },
 { text: "局限: 未深入语义维度, 忽视精英认知信息", options: { breakLine: true } },
 { text: "", options: { breakLine: true } },
 { text: "传统历史叙事", options: { bold: true, breakLine: true } },
 { text: "专家定性判断, 学术价值高", options: { breakLine: true } },
 { text: "局限: 缺乏可复现性, 无法量化验证", options: { breakLine: false } }
 ], {
 x: 0.6, y: 1.35, w: 4.1, h: 2.8,
 fontSize: 12, fontFace: "Microsoft YaHei",
 color: theme.primary, valign: "top", margin: 0
 });

 // Right panel - RQs
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 5.1, y: 0.75, w: 4.5, h: 4.3,
 fill: { color: theme.primary },
 rectRadius: 0.08
 });
 slide.addText("三个核心研究问题", {
 x: 5.3, y: 0.9, w: 4.1, h: 0.35,
 fontSize: 14, fontFace: "Microsoft YaHei",
 color: theme.bg, bold: true, margin: 0
 });

 const rqs = [
 { q: "RQ1", t: "小样本推断", a: "Bootstrap + Jeffreys先验\nAdjusted R\u00b2=0.36\n95%CI=(0.503, 0.731)" },
 { q: "RQ2", t: "古籍语义捕捉", a: "SikuBERT双模式\nernie-3.0-mini-zh接入\n降级兜底完好" },
 { q: "RQ3", t: "跨周期推广", a: "唐宋明+北宋\n四朝PSI一致\n危机区间验证" }
 ];
 rqs.forEach((r, i) => {
 const y = 1.4 + i * 1.15;
 slide.addText(r.q, {
 x: 5.3, y: y, w: 0.6, h: 0.35,
 fontSize: 12, fontFace: "Arial",
 color: theme.accent, bold: true, margin: 0
 });
 slide.addText(r.t, {
 x: 5.95, y: y, w: 3.4, h: 0.28,
 fontSize: 12, fontFace: "Microsoft YaHei",
 color: theme.bg, bold: true, margin: 0
 });
 slide.addText(r.a, {
 x: 5.95, y: y + 0.3, w: 3.4, h: 0.8,
 fontSize: 10, fontFace: "Microsoft YaHei",
 color: theme.light, margin: 0
 });
 if (i < 2) {
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 5.3, y: y + 1.05, w: 4.1, h: 0.01,
 fill: { color: theme.light, transparency: 60 }
 });
 }
 });

 // Bottom tagline
 slide.addText("本系统定位: 语义增强型文明预测, 差异化竞争Turchin定量框架", {
 x: 0.4, y: 5.1, w: 9.2, h: 0.3,
 fontSize: 11, fontFace: "Microsoft YaHei",
 color: theme.accent, italic: true, margin: 0
 });

 // Page number
 slide.addText("03", {
 x: 9.3, y: 5.1, w: 0.5, h: 0.35,
 fontSize: 10, fontFace: "Arial",
 color: theme.light, align: "right", valign: "middle"
 });
}
module.exports = { createSlide };
