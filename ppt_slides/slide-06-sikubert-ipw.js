function createSlide(pres, theme) {
 const slide = pres.addSlide();
 slide.background = { color: theme.bg };

 slide.addShape(pres.shapes.RECTANGLE, {
 x: 0, y: 0, w: 10, h: 0.55,
 fill: { color: theme.secondary }
 });
 slide.addText("04 SikuBERT古籍NLP + IPW偏差校正", {
 x: 0.5, y: 0, w: 9, h: 0.55,
 fontSize: 14, fontFace: "Microsoft YaHei",
 color: theme.bg, bold: true,
 valign: "middle", margin: 0
 });

 // Left: SikuBERT
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 0.4, y: 0.75, w: 4.4, h: 4.2,
 fill: { color: theme.light },
 rectRadius: 0.08
 });
 slide.addText("SikuBERT 双模式古籍NLP", {
 x: 0.55, y: 0.88, w: 4.1, h: 0.35,
 fontSize: 13, fontFace: "Microsoft YaHei",
 color: theme.secondary, bold: true, margin: 0
 });

 // Flow diagram
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 0.55, y: 1.35, w: 2.0, h: 0.42,
 fill: { color: theme.secondary },
 rectRadius: 0.05
 });
 slide.addText("ernie-3.0-mini-zh", {
 x: 0.55, y: 1.35, w: 2.0, h: 0.42,
 fontSize: 9, fontFace: "Arial",
 color: theme.bg, align: "center", valign: "middle"
 });
 slide.addText(">", {
 x: 2.55, y: 1.35, w: 0.3, h: 0.42,
 fontSize: 16, fontFace: "Arial",
 color: theme.secondary, align: "center", valign: "middle"
 });
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 2.85, y: 1.35, w: 1.8, h: 0.42,
 fill: { color: theme.accent },
 rectRadius: 0.05
 });
 slide.addText("规则词典兜底", {
 x: 2.85, y: 1.35, w: 1.8, h: 0.42,
 fontSize: 10, fontFace: "Microsoft YaHei",
 color: theme.bg, align: "center", valign: "middle"
 });

 // Test results
 const tests = [
 { text: "嘉祐之治, 天下太平", score: "+0.512", ok: true },
 { text: "百年积弊, 民不聊生", score: "-0.850", ok: false },
 { text: "天下太平, 百姓安乐", score: "+0.375", ok: true },
 { text: "民不聊生, 饿殍遍野", score: "-0.900", ok: false }
 ];
 slide.addText("验证结果(降级模式)", {
 x: 0.55, y: 1.95, w: 4.1, h: 0.3,
 fontSize: 10, fontFace: "Microsoft YaHei",
 color: theme.secondary, bold: true, margin: 0
 });
 tests.forEach((t, i) => {
 const y = 2.28 + i * 0.6;
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 0.55, y: y, w: 4.1, h: 0.5,
 fill: { color: theme.bg },
 rectRadius: 0.04
 });
 slide.addText(t.score, {
 x: 0.65, y: y, w: 0.8, h: 0.5,
 fontSize: 13, fontFace: "Arial",
 color: t.ok ? "34d399" : "f87171",
 bold: true, valign: "middle", margin: 0
 });
 slide.addText(t.text, {
 x: 1.5, y: y, w: 2.5, h: 0.5,
 fontSize: 10, fontFace: "Microsoft YaHei",
 color: theme.primary, valign: "middle", margin: 0
 });
 slide.addText(t.ok ? "POS" : "NEG", {
 x: 4.05, y: y, w: 0.5, h: 0.5,
 fontSize: 9, fontFace: "Arial",
 color: t.ok ? "34d399" : "f87171",
 bold: true, valign: "middle", align: "center"
 });
 });

 // Note
 slide.addText("pip install transformers 后自动激活真实模型", {
 x: 0.55, y: 4.65, w: 4.1, h: 0.22,
 fontSize: 9, fontFace: "Microsoft YaHei",
 color: theme.light, italic: true, margin: 0
 });

 // Right: IPW
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 5.1, y: 0.75, w: 4.5, h: 4.2,
 fill: { color: theme.secondary },
 rectRadius: 0.08
 });
 slide.addText("CBDB IPW 逆概率加权偏差校正", {
 x: 5.25, y: 0.88, w: 4.2, h: 0.35,
 fontSize: 13, fontFace: "Microsoft YaHei",
 color: theme.bg, bold: true, margin: 0
 });
 slide.addText("倾向分模型", {
 x: 5.25, y: 1.35, w: 4.2, h: 0.25,
 fontSize: 10, fontFace: "Microsoft YaHei",
 color: theme.light, margin: 0
 });
 slide.addText("propensity = sigmoid(0.3 + rank_bonus + north_bonus + school_bonus)", {
 x: 5.25, y: 1.62, w: 4.2, h: 0.3,
 fontSize: 9, fontFace: "Arial",
 color: theme.accent, margin: 0
 });

 const biasItems = [
 { label: "高品级(三品+)", bonus: "+0.50", desc: "传记记载更完整" },
 { label: "北方籍贯(>=34N)", bonus: "+0.40", desc: "政治中心在北方" },
 { label: "主流学派(儒家)", bonus: "+0.30", desc: "话语权更大" }
 ];
 biasItems.forEach((b, i) => {
 const y = 2.0 + i * 0.58;
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 5.25, y: y, w: 4.2, h: 0.5,
 fill: { color: theme.bg, transparency: 85 },
 rectRadius: 0.04
 });
 slide.addText(b.label, {
 x: 5.35, y: y, w: 2.2, h: 0.5,
 fontSize: 10, fontFace: "Microsoft YaHei",
 color: theme.bg, valign: "middle", margin: 0
 });
 slide.addText(b.bonus, {
 x: 7.55, y: y, w: 0.6, h: 0.5,
 fontSize: 12, fontFace: "Arial",
 color: theme.accent, bold: true, valign: "middle", align: "center"
 });
 slide.addText(b.desc, {
 x: 8.2, y: y, w: 1.2, h: 0.5,
 fontSize: 9, fontFace: "Microsoft YaHei",
 color: theme.light, valign: "middle", margin: 0
 });
 });

 // Result highlight
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 5.25, y: 3.85, w: 4.2, h: 0.85,
 fill: { color: theme.accent },
 rectRadius: 0.06
 });
 slide.addText("校正结论", {
 x: 5.4, y: 3.95, w: 1.2, h: 0.3,
 fontSize: 10, fontFace: "Microsoft YaHei",
 color: theme.bg, bold: true, margin: 0
 });
 slide.addText("PSI 0.614 > 0.604 下降 1.6%", {
 x: 5.4, y: 4.22, w: 3.9, h: 0.4,
 fontSize: 16, fontFace: "Arial",
 color: theme.bg, bold: true, margin: 0
 });

 // Page number
 slide.addText("06", {
 x: 9.3, y: 5.1, w: 0.5, h: 0.35,
 fontSize: 10, fontFace: "Arial",
 color: theme.light, align: "right", valign: "middle"
 });
}
module.exports = { createSlide };
