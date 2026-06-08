function createSlide(pres, theme) {
 const slide = pres.addSlide();
 slide.background = { color: theme.bg };

 slide.addShape(pres.shapes.RECTANGLE, {
 x: 0, y: 0, w: 10, h: 0.55,
 fill: { color: theme.secondary }
 });
 slide.addText("06 IPW偏差校正详细效果", {
 x: 0.5, y: 0, w: 9, h: 0.55,
 fontSize: 14, fontFace: "Microsoft YaHei",
 color: theme.bg, bold: true,
 valign: "middle", margin: 0
 });

 // 5 experts data
 const experts = [
 { name: "Simaguang", label: "司马光", psi: 0.800, prop: 0.731, weight: 1.368, corr: 0.742, type: "down" },
 { name: "Fanzhongyan", label: "范仲淹", psi: 0.720, prop: 0.646, weight: 1.549, corr: 0.756, type: "down" },
 { name: "Ouyangxiu", label: "欧阳修", psi: 0.650, prop: 0.750, weight: 1.333, corr: 0.588, type: "mid" },
 { name: "Wanganshi", label: "王安石", psi: 0.400, prop: 0.574, weight: 1.741, corr: 0.473, type: "up" },
 { name: "Sushi", label: "苏轼", psi: 0.500, prop: 0.690, weight: 1.449, corr: 0.492, type: "up" }
 ];

 // Column headers
 const cols = [
 { label: "专家", x: 0.4, w: 1.3 },
 { label: "PSI原始", x: 1.7, w: 1.1 },
 { label: "倾向分", x: 2.8, w: 1.0 },
 { label: "逆权重", x: 3.8, w: 1.0 },
 { label: "校正后PSI", x: 4.8, w: 1.3 },
 { label: "效果", x: 6.1, w: 1.2 },
 { label: "偏差类型", x: 7.3, w: 2.3 }
 ];

 // Header row
 cols.forEach((c) => {
 slide.addShape(pres.shapes.RECTANGLE, {
 x: c.x, y: 0.72, w: c.w, h: 0.38,
 fill: { color: theme.secondary }
 });
 slide.addText(c.label, {
 x: c.x, y: 0.72, w: c.w, h: 0.38,
 fontSize: 10, fontFace: "Microsoft YaHei",
 color: theme.bg, bold: true, align: "center", valign: "middle"
 });
 });

 experts.forEach((e, i) => {
 const y = 1.1 + i * 0.68;
 const bgColor = i % 2 === 0 ? theme.light : theme.bg;

 // Name
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 0.4, y: y, w: 1.3, h: 0.62,
 fill: { color: bgColor }
 });
 slide.addText(e.label, {
 x: 0.4, y: y, w: 1.3, h: 0.62,
 fontSize: 12, fontFace: "Microsoft YaHei",
 color: theme.primary, bold: true, align: "center", valign: "middle"
 });

 // PSI raw
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 1.7, y: y, w: 1.1, h: 0.62,
 fill: { color: bgColor }
 });
 slide.addText(e.psi.toFixed(3), {
 x: 1.7, y: y, w: 1.1, h: 0.62,
 fontSize: 13, fontFace: "Arial",
 color: theme.accent, bold: true, align: "center", valign: "middle"
 });

 // Propensity
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 2.8, y: y, w: 1.0, h: 0.62,
 fill: { color: bgColor }
 });
 slide.addText(e.prop.toFixed(3), {
 x: 2.8, y: y, w: 1.0, h: 0.62,
 fontSize: 12, fontFace: "Arial",
 color: theme.primary, align: "center", valign: "middle"
 });

 // Weight
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 3.8, y: y, w: 1.0, h: 0.62,
 fill: { color: bgColor }
 });
 slide.addText(e.weight.toFixed(3), {
 x: 3.8, y: y, w: 1.0, h: 0.62,
 fontSize: 12, fontFace: "Arial",
 color: theme.primary, align: "center", valign: "middle"
 });

 // Corrected PSI
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 4.8, y: y, w: 1.3, h: 0.62,
 fill: { color: bgColor }
 });
 slide.addText(e.corr.toFixed(3), {
 x: 4.8, y: y, w: 1.3, h: 0.62,
 fontSize: 13, fontFace: "Arial",
 color: e.type === "up" ? "34d399" : e.type === "down" ? "f87171" : theme.primary,
 bold: true, align: "center", valign: "middle"
 });

 // Effect badge
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 6.1, y: y + 0.12, w: 1.2, h: 0.38,
 fill: { color: e.type === "up" ? "34d399" : e.type === "down" ? "f87171" : theme.light },
 rectRadius: 0.04
 });
 slide.addText(e.type === "up" ? "UP" : e.type === "down" ? "DOWN" : "MID", {
 x: 6.1, y: y + 0.12, w: 1.2, h: 0.38,
 fontSize: 10, fontFace: "Arial",
 color: e.type === "mid" ? theme.primary : theme.bg, bold: true,
 align: "center", valign: "middle"
 });

 // Bias type
 const biasLabels = {
 down: "高偏差(北方+高品级+主流)",
 up: "低偏差(南方+新学+低品级)",
 mid: "中等偏差"
 };
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 7.3, y: y, w: 2.3, h: 0.62,
 fill: { color: bgColor }
 });
 slide.addText(biasLabels[e.type], {
 x: 7.4, y: y, w: 2.1, h: 0.62,
 fontSize: 10, fontFace: "Microsoft YaHei",
 color: theme.primary, valign: "middle", margin: 0
 });

 // Row border
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 0.4, y: y + 0.62, w: 9.2, h: 0.02,
 fill: { color: theme.light }
 });
 });

 // Bottom summary
 slide.addShape(pres.shapes.RECTANGLE, {
 x: 0.4, y: 4.7, w: 6.4, h: 0.7,
 fill: { color: theme.secondary },
 rectRadius: 0.06
 });
 slide.addText("加权平均 PSI", {
 x: 0.55, y: 4.78, w: 2.5, h: 0.25,
 fontSize: 11, fontFace: "Microsoft YaHei",
 color: theme.light, margin: 0
 });
 slide.addText("0.614 > 0.604", {
 x: 0.55, y: 5.0, w: 3.0, h: 0.35,
 fontSize: 20, fontFace: "Arial",
 color: theme.accent, bold: true, margin: 0
 });
 slide.addText("下降 1.6% 验证通过", {
 x: 3.6, y: 5.0, w: 3.0, h: 0.35,
 fontSize: 14, fontFace: "Arial",
 color: theme.bg, bold: true, valign: "middle", margin: 0
 });

 // Page number
 slide.addText("08", {
 x: 9.3, y: 5.1, w: 0.5, h: 0.35,
 fontSize: 10, fontFace: "Arial",
 color: theme.light, align: "right", valign: "middle"
 });
}
module.exports = { createSlide };
