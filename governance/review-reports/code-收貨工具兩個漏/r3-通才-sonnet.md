severity: blocker

## F1 找 F 段標題的正則丟了原本容許的行首縮排,縮排過的 F 標題整段連同漏寫的 severity 一起被吃掉(silent false negative)

severity: blocker
blocking: yes

`_report_findings_missing_severity` 重寫時,新的 `heads` 掃描正則把舊正則開頭的 `\s*`(行首可有縮排)拿掉了:

引句:「heads = [(no, ln, len(m.group(1))) for no, ln in _visible_lines(lines, keep_fenced=False)」
引句:「for m in [re.match(r"^(#{2,6})\s*F\d+\b", ln, re.I)] if m]」

對照被刪掉的舊版本(patch 同一段的 `-` 行),舊正則是 `^\s*#{2,6}\s*F\d+\b`,`#` 前面允許縮排;新正則是 `^(#{2,6})\s*F\d+\b`,`#` 必須頂格,少了同一個 `\s*`。CommonMark 允許 ATX 標題前面縮排 0–3 格且渲染結果不變,舊版本本來接得住,這次重寫在接縫處把它弄丟了。

翻紅重現(在 /tmp 複本套用此 patch 後實跑):
```
$ cat > /tmp/rn3-tests/t2.md << 'EOF'
severity: blocker

  ## F1 縮排標題,故意漏寫嚴重度
引句:「這是一段足夠長的引句內容」
EOF
$ python3 scripts/lumos report-normalize /tmp/rn3-tests/t2.md
✓ /tmp/rn3-tests/t2.md 已是正規化格式(檔級行在檔首、每條 finding 一行 severity),不用改
```
檔首宣告 `severity: blocker` 且 F1 整段沒有任何 `severity:` 行,只因標題前多了兩個空格,收貨檢查就判成「已正規化,不用改」(rc0)——正是這支工具要擋的那個洞(「F1、F2 都漏寫在收貨偵測被說成已正規化」)又從另一個輸入形狀重新打開,而且是靜默通過,不是誤擋,危害方向比誤擋更嚴重。

## F2 finding 標題正則對 `F\d+` 用 `\b` 收尾,子節/延伸標題只要跟在數字後面接非文字字元(句點、連字號)就會被誤認成新的一個「finding 標題」,把前一條真正的 F 段邊界腰斬,severity 明明寫了卻被判缺

severity: major
blocking: yes

引句:「end = heads[idx + 1][0] if idx + 1 < len(heads) else float("inf")」

`heads` 用 `re.match(r"^(#{2,6})\s*F\d+\b", ln, re.I)` 抓「發現標題」,`\d+` 後面只要接非文字字元(句點、連字號、空白、冒號…)就過 `\b`。本 repo 既有審查報告就有「### F1. …」這種 F 後面直接接句點的標題慣例(見 `governance/review-reports/規格落成可驗收條件/r5-邊界5-sonnet.md:13`、`governance/review-reports/code-codex-refine/r1-邊界可執行.md:7`),若 F 段裡再帶一個編號子標題(例如重現步驟另開 `### F1.1 …`),`F1.1` 一樣會被這個正則當成又一個「F1」標題收進 `heads`,把原本 F1 的搜尋上界(`end`)提前腰斬到子標題那一行。

翻紅重現:
```
$ cat > /tmp/rn3-tests/t1.md << 'EOF'
severity: major

## F1 一條
### F1.1 子細節
severity: major
blocking: yes
引句:「這是一段足夠長的引句內容」
EOF
$ python3 scripts/lumos report-normalize /tmp/rn3-tests/t1.md
會改 0 處(加 --write 才寫回):
⚠ 還有 1 處機器轉不了,要人改(不然 canary record 會擋):
    第 3 行:這條發現沒有自己的一行 severity: <值>(檔首判成非 clean 時,每個 F 段都要有;要請審查席自己補)
      ## F1 一條
```
F1 明明在第 5 行寫了 `severity: major`,卻因為第 4 行的 `### F1.1 子細節` 被誤判成另一個發現標題、把 F1 的搜尋範圍截到第 4 行之前(第 5 行的 severity 落在範圍外),被誤擋要人改。這是給合法報告的假阻擋,方向與 F1 相反但成因同源(同一顆正則對 `F\d+` 太寬鬆)。

## 已驗過、沒問題的部分
引句:「check("⑩ ## Findings 底下用 ### F 的合法報告不誤擋(四級子標題也不切段)", r.returncode == 0, r.stdout[-400:])」
patch 裡新增的九支斷言(①~⑪ 減掉沿用舊案例的部分,含 lower/sub/loose/depth/h3/seen/dup)我在 /tmp 複本上用 `python3 scripts/lumos report-normalize <各檔>` 逐一重跑過,結果都跟斷言一致,沒有異常。`_FINDING_VERIFIED_WORDS` 改成完整片語後,「已看,無」與「已看，無」兩種逗號寫法都能豁免,拿掉單獨「已讀」「已看」不影響本輪找到的兩個洞。`loop next` 印的記帳模板(`record_cmd`/`disposal_cmd` 改用 `none`、補 `--snapshot`)不在這份 r3 diff 內(相對 341327c5 沒有變動),不屬於本輪修正範圍,未重審。
