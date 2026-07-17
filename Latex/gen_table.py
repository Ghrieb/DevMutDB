import csv, sys

rows = list(csv.DictReader(open(r'C:\Users\Hani\Desktop\DevMutDB\validation\benchmark_results.csv', encoding='utf-8')))

dev = [r for r in rows if r['class'] == 'developmental']
adult = [r for r in rows if r['class'] == 'adult']

def fmt(v, decimals=1):
    if v == '' or v is None or v == 'None':
        return '---'
    f = float(v)
    if decimals == 0:
        return '%d' % int(f)
    if decimals == 3:
        return '%.3f' % f
    tpl = '%%.%df' % decimals
    return tpl % f

out = []
out.append('% --- Supplementary Table S1 ---')
out.append('\\onecolumn')
out.append('\\section*{Supplementary Table S1: Full Validation Cohort}')
out.append('\\label{tab:supplementary_s1}')
out.append('')
out.append('\\vspace{2mm}')
out.append('\\noindent')
out.append('\\begin{minipage}[t]{0.48\\textwidth}')
out.append('\\centering{Part A: Developmental disease genes (n = 60)} \\\\')
out.append('\\vspace{1mm}')
out.append('\\footnotesize')
out.append('\\setlength{\\tabcolsep}{1.5pt}')
out.append('\\renewcommand{\\arraystretch}{0.75}')
out.append('\\resizebox{\\linewidth}{!}{%')
out.append('\\begin{tabular}{@{}llrrrrrr@{}}')
out.append('\\toprule')
out.append('\\# & Gene & DevScore & V & E$_{\\mathrm{peak}}$ & C$_{\\mathrm{stage}}$ & D$_{\\mathrm{domain}}$ & CADD \\\\')
out.append('\\midrule')
for i, r in enumerate(dev, 1):
    out.append('  %3d  & %-8s & %s & %s & %s & %s & %s & %s \\\\' % (
        i, r['gene'],
        fmt(r['devscore']),
        fmt(r['V'], 3) if r['V'] and r['V'] != 'None' else fmt(r['V'], 2),
        fmt(r['E_peak'], 2),
        fmt(r['C_stage'], 2),
        fmt(r['D_domain'], 1),
        fmt(r['cadd'], 1)))
out.append('\\bottomrule')
out.append('\\end{tabular}')
out.append('}')
out.append('\\end{minipage}')
out.append('\\hfill')
out.append('\\begin{minipage}[t]{0.48\\textwidth}')
out.append('\\centering{Part B: Adult-onset genes (n = 50)} \\\\')
out.append('\\vspace{1mm}')
out.append('\\footnotesize')
out.append('\\setlength{\\tabcolsep}{1.5pt}')
out.append('\\renewcommand{\\arraystretch}{0.75}')
out.append('\\resizebox{\\linewidth}{!}{%')
out.append('\\begin{tabular}{@{}llrrrrrr@{}}')
out.append('\\toprule')
out.append('\\# & Gene & DevScore & V & E$_{\\mathrm{peak}}$ & C$_{\\mathrm{stage}}$ & D$_{\\mathrm{domain}}$ & CADD \\\\')
out.append('\\midrule')
for i, r in enumerate(adult, 1):
    out.append('  %3d  & %-8s & %s & %s & %s & %s & %s & %s \\\\' % (
        i, r['gene'],
        fmt(r['devscore']),
        fmt(r['V'], 3) if r['V'] and r['V'] != 'None' else fmt(r['V'], 2),
        fmt(r['E_peak'], 2),
        fmt(r['C_stage'], 2),
        fmt(r['D_domain'], 1),
        fmt(r['cadd'], 1)))
out.append('\\bottomrule')
out.append('\\end{tabular}')
out.append('}')
out.append('\\end{minipage}')
out.append('')
out.append('\\vspace{2mm}')
out.append('\\begin{center}')
out.append('{\\footnotesize Abbreviations: V, variant severity; E$_{\\mathrm{peak}}$, peak developmental expression; C$_{\\mathrm{stage}}$, developmental stage criticality; D$_{\\mathrm{domain}}$, protein domain essentiality.}')
out.append('\\end{center}')
out.append('\\clearpage')
out.append('')
out.append('\\end{document}')

sys.stdout.write('\n'.join(out))
