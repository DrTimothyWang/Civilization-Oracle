function createSlide(pres, theme) {
 const slide = pres.addSlide();
 slide.background = { color: theme.bg };

 slide.addShape(pres.shapes.RECTANGLE, {
 x: 0, y: 0, w: 10, h: 0.55,
 fill: { color: theme.secondary }
 });
 slide.addText("07 关键发现与学术贡献", {
 x: 0.5, y: 0, w: 9, h: 0.55,
 fontSize: 14, fontFace: "Microsoft YaHei",
 color: theme.bg, bold: true,
 valign: "middle", margin: 0
 });

 // Key findings - 3 columns
 const findings = [
 {
 icon: "1",
 title: "四朝PSI危机区间一致性",
 body: "唐宋明+北宋四朝PSI校正值一致落在0.24-0.33区间, 初步验证了PSI跨朝代可推广性, 支持SDT理论核心假设."
 },
 {
 icon: "2",
 title: "IPW有效识别CBDB偏差",
 body: "高选择偏差样本(北方+高品级+主流学派)被正确降权, PSI下降1.6%, CBDB偏差首次被量化校正."
 },
 {
 icon: "3",
 title: "贝叶斯框架解决小样本",
 body: "Bootstrap 2000次重抽样 + Jeffreys先验, Adjusted R\u00b2=0.36揭示原始高估, 95%CI=(0.503, 0.731)."
 }
 ];

 findings.forEach((f, i) => {
 const x = 0.4 + i * 3.15;
 slide.addShape(pres.shapes.RECTANGLE, {
 x: x, y: 0.75, w: 3.0, h: 2.8,
 fill: { color: theme.light },
 rectRadius: 0.08
 });
 // Icon
 slide.addShape(pres.shapes.OVAL, {
 x: x + 0.15, y: 0.9, w: 0.45, h: 0.45,
 fill: { color: theme.secondary }
 });
 slide.addText(f.icon, {
 x: x + 0.15, y: 0.9, w: 0.45, h: 0.45,
 fontSize: 16, fontFace: "Arial",
 color: theme.bg, bold: true, align: "center", valign: "middle"
 });
 slide.addText(f.title, {
 x: x + 0.15, y: 1.45, w: 2.7, h: 0.55,
 fontSize: 13, fontFace: "Microsoft YaHei",
 color: theme.secondary, bold: true, margin: 0
 });
 slide.addText(f.body, {
 x: x + 0.15, y: 2.0, w: 2.7, h: 1.4,
 fontSize: 11, fontFace: "Microsoft YaHei",
 color: theme.primary, margin: 0
 });
 });

 // Comparison table
 slide.addText("与Cliodynamics差异对比", {
 x: 0.4, y: 3.75, w: 9.2, h: 0.3,
 fontSize: 12, fontFace: "Microsoft YaHei",
 color: theme.secondary, bold: true, margin: 0
 });

 const compData = [
 ["维度", "Turchin / Seshat", "Civilization-Oracle"],
 ["核心驱动", "人口经济学(BA)", "语义心理学(SDT/PSI)"],
 ["方法论", "OLS回归", "贝叶斯+IPW"],
 ["偏差校正", "无", "IPW逆概率加权"],
 ["语义深度", "无", "SikuBERT+CPM-KB"],
 ["中国数据", "有限", "核心优势"]
 ];

 const cw = [1.5, 3.0, 3.0];
 const compY = 4.1;
 const rh = 0.28;
 compData.forEach((row, ri) => {
 const isH = ri === 0;
 row.forEach((cell, ci) => {
 const x = 0.4 + ci * 2.5;
 slide.addShape(pres.shapes.RECTANGLE, {
 x: x, y: compY + ri * rh, w: cw[ci], h: rh,
 fill: { color: isH ? theme.secondary : (ri % 2 === 0 ? theme.light : theme.bg) }
 });
 slide.addText(cell, {
 x: x + 0.05, y: compY + ri * rh, w: cw[ci] - 0.05, h: rh,
 fontSize: 9, fontFace: ci === 0 ? "Microsoft YaHei" : "Arial",
 color: isH ? theme.bg : (ci === 2 ? theme.accent : theme.primary),
 bold: isH || ci === 2, valign: "middle", margin: 0
 });
 });
 });

 // Page number
 slide.addText("09", {
 x: 9.3, y: 5.1, w: 0.5, h: 0.35,
 fontSize: 10, fontFace: "Arial",
 color: theme.light, align: "right", valign: "middle"
 });
}
module.exports = { createSlide };
