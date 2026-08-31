# code-revisit r1 通才席(standard 循序單席)
H-1|major|blocking:是:E5 摘要 f-string 直印零消毒——ANSI/BEL 注入實測穿透(兩天前 _esc_clean 修過同洞,回歸)。
引句:「_lines5 = [f"{d} {sm}(逾 {ag} 天)← {st}" for ag, d, sm, st in _rv_due]」
H-2|minor:壞日期提示會被 cap3 吞進「另 N 條」,與 fail-closed 宣稱落差;測試沒蓋 cap 邊界。
引句:「全靜默:0 到期 0 壞行整段不印。」
H-3|informational:--ci 使 rc 反映真 issues(裸 doctor 恆 0)——daily 腳本 rc 只 echo 不判,現況無誤觸發;後人接 rc 告警要知道它含全部硬 check。
H-4|clean:E5 增量掃描 0.8s/390 篇,同函式既有量級。
H-5|clean:表格/巢狀 bullet 順序實測正確;`- [ ]` 勾選框吃不到=照 spec(T1 只列 -/*)。
H-6:壞日期紅釘突變驗證翻紅還原淨空。
severity: major
