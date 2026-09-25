severity: major

## F1 標題是小寫 f 時整段漏寫 severity 也不會被抓到(誤放行)
severity: major
blocking: yes
引句:「if re.match(r"^\s*#{2,6}\s*F\d+\b", ln) and not any(w in ln for w in _FINDING_VERIFIED_WORDS):」
判定「這是一條發現段」的正則 `F\d+` 沒有 `re.I`,只認大寫 `F`。拿一份標題寫成 `## f1 小寫F開頭發現`、且完全沒有 `severity:` 行的報告去跑,`report-normalize` 判成「已正規化,不用改」(rc0)。這正是這個工具存在的理由——抓「F 段漏寫 severity」——卻因為大小寫不同就整段隱形,連 _report_findings_missing_severity 都沒開始追蹤它。
翻紅重現(在 /tmp 複本跑,rc0 即代表誤放行):
```
cd /tmp/rn-test/repo
cat > /tmp/rn-test/repo/lowercase.md <<'EOF'
severity: major

## f1 小寫F開頭發現
引句:「這是一段足夠長的引句內容,但沒有寫severity」
EOF
python3 scripts/lumos report-normalize /tmp/rn-test/repo/lowercase.md   # 輸出「已是正規化格式」,rc=0
```

## F2 F 段裡插一個子標題,severity 行就算白寫,合法報告被誤擋
severity: major
blocking: yes
引句:「elif cur is not None and _SEV_DECL_LINE_RE.fullmatch(ln):」
`_report_findings_missing_severity` 用「任何標題(`#{1,6}`)都會把目前追蹤的 F 段關掉」來判斷一段結束,但很多真報告會在一條發現底下再開一個三/四層子標題(例如「### 細節」)分段說明,severity 行接在子標題後面才寫。子標題一出現,`cur` 就被清空,之後那行真正存在的 `severity: major` 不會被算進去,F1 被判成「沒有自己的一行 severity」而擋下(rc1),即使報告完全照格式寫了。
翻紅重現:
```
cd /tmp/rn-test/repo
cat > /tmp/rn-test/repo/subheading.md <<'EOF'
severity: major

## F1 一條發現
### 細節
補充說明文字在這裡。
severity: major
blocking: yes
引句:「這是一段足夠長的引句內容」
EOF
python3 scripts/lumos report-normalize /tmp/rn-test/repo/subheading.md
# 輸出:第 3 行:這條發現沒有自己的一行 severity...(rc=1),但這份報告其實有寫 severity
```

## 已驗過、沒問題的部分
引句:「lumos canary record none --loop {_qid}{rmode} --auditor <席> --severity <s> --findings <M>」
以下場景實測都如作者宣稱一樣正常,沒有問題:
- 多個 F 共用一份 severity(F1 沒有自己的行、severity 只接在 F2 後面)→ 正確判成 F1 缺,不算漏抓。
- F 段整段被圍欄(```)包住(例如引用別份報告當範例)→ `_visible_lines(keep_fenced=False)` 把圍欄內容整段當隱形,不會誤判成真發現,也不會讓圍欄裡的假 severity 頂替真發現。
- 標題含「已驗過/沒問題」(`_FINDING_VERIFIED_WORDS`)的 F 段確實被排除,不強制要 severity。
- `severity:` 行前面帶縮排(如 `  severity: major`)這種格式殘留,是 `normalize_report_text` 本身就會先重寫拉平,不會走到 `_report_findings_missing_severity` 誤判缺失,行為符合預期。
- `loop next` 的 record_cmd 在 design/code 的 standard、legacy、light 分級下都帶了 `--snapshot`,且是同一段程式碼統一輸出(不分 tier 另寫),實測 light 分級把模板填完 `lumos canary record none ... --snapshot <spec> ...` 真的能跑到 rc0(見下方指令),legacy/standard 兩型已有既有測試 `t_loop_next_disposal_cmd_actually_runs`、`t_loop_next_legacy_emits_a_command_that_actually_runs` 覆蓋過。
```
cd /tmp/rn-test/repo && python3 scripts/lumos loop next 'code-light測試-abc123' --tier light --orchestrator claude --json
# record_cmd 內含 --snapshot <凍結快照.md>,填完值真的跑得動(rc0,已實測)
```
