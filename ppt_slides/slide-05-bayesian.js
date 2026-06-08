function createSlide(pres, theme) {
 const slide = pres.addSlide();
 slide.background = { color: theme.bg };

 slide.addShape(pres.shapes.RECTANGLE, {
 x: 0, y: 0, w: 10, h: 0.55,
 fill: { color: theme.secondary }
 });
 slide.addText("03 PSI贝叶斯推断框架", {
 x: 0.5, y: 0, w: 9, h: 0.55,
 fontSize: 14, fontFace: "Microsoft YaHei",
 color: theme.bg, bold: true,
 valign: "middle", margin: 0
 });

 // Problem diagnosis
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 0.4, y: 0.75, w: 4.4, h: 1.5,
 fill: { color: theme.accent, transparency: 15 },
 rectRadius: 0.06
 });
 slide.addText("问题诊断", {
 x: 0.55, y: 0.85, w: 4.1, h: 0.3,
 fontSize: 12, fontFace: "Microsoft YaHei",
 color: theme.accent, bold: true, margin: 0
 });
 slide.addText("OLS回归对北宋7周期数据R\u00b2=0.68, 调整后Adjusted R\u00b2仅为0.36, 揭示典型过拟合陷阱: 小样本(n=7, k=3)导致置信区间过窄, 模型解释力被严重高估.", {
 x: 0.55, y: 1.15, w: 4.1, h: 1.0,
 fontSize: 11, fontFace: "Microsoft YaHei",
 color: theme.primary, margin: 0
 });

 // Solution
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 5.1, y: 0.75, w: 4.5, h: 1.5,
 fill: { color: theme.secondary },
 rectRadius: 0.06
 });
 slide.addText("解决方案", {
 x: 5.25, y: 0.85, w: 4.2, h: 0.3,
 fontSize: 12, fontFace: "Microsoft YaHei",
 color: theme.bg, bold: true, margin: 0
 });
 slide.addText("Bootstrap 2000次重抽样 + Jeffreys无信息先验 + Hedges' g小样本修正 + SFD权重0.50", {
 x: 5.25, y: 1.15, w: 4.2, h: 1.0,
 fontSize: 11, fontFace: "Microsoft YaHei",
 color: theme.bg, margin: 0
 });

 // Results table
 slide.addText("验证结果(北宋7周期)", {
 x: 0.4, y: 2.45, w: 9, h: 0.3,
 fontSize: 12, fontFace: "Microsoft YaHei",
 color: theme.secondary, bold: true, margin: 0
 });

 const tableRows = [
 ["指标", "原始值", "贝叶斯校正"],
 ["PSI均值", "0.6309", "0.6309"],
 ["PSI标准差", "未报告", "0.0584"],
 ["95%CI", "未报告", "(0.503, 0.731)"],
 ["Adjusted R\u00b2", "0.36", "0.36"]
 ];
 const colWidths = [2.2, 2.2, 2.2];
 const tableX = 0.5;
 const tableY = 2.8;
 const rowH = 0.38;

 tableRows.forEach((row, ri) => {
 const isHeader = ri === 0;
 row.forEach((cell, ci) => {
 const x = tableX + ci * 2.2;
 slide.addShape(pres.shapes.RECTANGLE, {
 x: x, y: tableY + ri * rowH, w: colWidths[ci], h: rowH,
 fill: { color: isHeader ? theme.secondary : (ri % 2 === 0 ? theme.light : theme.bg) },
 line: { color: theme.light, width: 0.5 }
 });
 slide.addText(cell, {
 x: x + 0.08, y: tableY + ri * rowH, w: colWidths[ci] - 0.08, h: rowH,
 fontSize: 11, fontFace: isHeader ? "Arial" : "Microsoft YaHei",
 color: isHeader ? theme.bg : theme.primary,
 bold: isHeader, valign: "middle", margin: 0
 });
 });
 });

 // Key insight
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 7.2, y: 2.8, w: 2.4, h: 1.9,
 fill: { color: theme.primary },
 rectRadius: 0.06
 });
 slide.addText("核心洞察", {
 x: 7.35, y: 2.92, w: 2.1, h: 0.28,
 fontSize: 11, fontFace: "Microsoft YaHei",
 color: theme.bg, bold: true, margin: 0
 });
 slide.addText("SFD权重\n从0.33\n提升至0.50", {
 x: 7.35, y: 3.25, w: 2.1, h: 1.3,
 fontSize: 18, fontFace: "Arial",
 color: theme.accent, bold: true, margin: 0
 });

 // Page number
 slide.addText("05", {
 x: 9.3, y: 5.1, w: 0.5, h: 0.35,
 fontSize: 10, fontFace: "Arial",
 color: theme.light, align: "right", valign: "middle"
 });
}
module.exports = { createSlide };
