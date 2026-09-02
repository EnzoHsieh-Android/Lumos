# metric-guard code r2 終態席(全新)
F2-1|minor:兩掃描面過濾不對稱——autonomous_loop 遞迴化漏掛 pycache 排除(實查 11 顆 .pyc 在口子裡;.pyc 常量夾帶字面會成打不掉的偽陽性)。
引句:「scan += [q for q in al.rglob("*") if q.is_file()] if al.exists() else []」
抑噪:日期字典序=時間序成立;同日 tie-break 穩定排序驗過;掃描面 33+26 檔 0.0s;4 綠。
severity: minor
