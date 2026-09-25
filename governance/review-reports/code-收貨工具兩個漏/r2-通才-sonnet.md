severity: major

## F1 相鄰 F 段標題層級不一致時,前一段的缺 severity 會被後一段的 severity 行頂替掉,漏抓

`_report_findings_missing_severity` 用單一變數 `cur`/`cur_lv` 追蹤「目前正在等 severity 的那一段」,遇到更深層標題就 `continue`(視為子標題、不換段)。但這個判斷只比較層級數字,不管這個更深標題是不是另一個 `F<n>`。當報告把第二個 finding 誤寫成比前一個更深的層級(例如 `## F1` 後接 `### F2`,而不是同層的 `## F2`),`F2` 的標題行會被吞進「continue」分支,既不會結束 `F1` 的段落、也不會替 `F2` 另起一段。接著 `F2` 底下若真的寫了 `severity:` 行,這行會被當成收尾 `cur`(語意上仍是 F1 在等的那個)——於是 `F1` 實際沒有自己的 severity,卻被判成「已正規化」放行;而 `F2` 也從沒被獨立檢查過(它從未被設成 `cur`)。

翻紅重現:
```
severity: major

## F1 一條
### F2 二條
severity: major
blocking: yes
```
用 repo 現有的 `_report_findings_missing_severity` 直接呼叫:
```python
mod._report_findings_missing_severity(text.splitlines(), "major")  # -> []
```
跑到底:
```
$ python3 scripts/lumos report-normalize bug.md
✓ .../bug.md 已是正規化格式(檔級行在檔首、每條 finding 一行 severity),不用改
rc=0
```
F1 完全沒有 severity 行,檔首宣告 `major`(非 clean),照這支 patch 想修的行為(2026-09-25 那個動機:F1、F2 都漏寫卻被說成已正規化),本該被擋,但因為 F2 的標題比 F1 深一層,反而放行——正是這支 r1→r2 修法自己補「子標題不切斷段落」時,在接縫處新開的洞:它只認「層級數字」,不認「是不是另一個 F」。

引句:「if cur is not None and lv > cur_lv:」

這個場景不算太離奇:審查席報告常是人或 AI 邊寫邊調整標題階層,兩個 finding 用了不同層級(例如第一個手動打 `##`、第二個複製舊範本殘留成 `###`)是完全可能發生的格式手誤,而且正好是這支工具存在的目的——防止「格式手誤讓漏寫 severity 溜過去」。

severity: major
blocking: yes

## 已驗過、沒問題的部分

- 「F 不分大小寫」(`f1` vs `F1`):讀了 `re.match(...F\d+\b", ln, re.I)`,ⓔ 測試案例(lower.md)跑過確認會抓到,沒問題。
- 「子標題不切斷段落」本身(F 段裡 `### 重現` 之類子標題,severity 寫在子標題下面):同層級比較邏輯在「單一 F 段內部深度單調遞增再回收」的正常寫法下是對的,ⓕ 測試(sub.md)驗證通過。
- 「已讀」豁免詞被拿掉單獨列(只留「已讀取失敗」不被誤豁免、「已讀,無 finding」靠「無 finding」涵蓋):ⓖ 測試(loose.md)驗證通過,`_FINDING_VERIFIED_WORDS` 確實已改成 `("已驗過", "沒問題", "無 finding")`,不含單獨「已讀」「已看」。
- 圍欄內的 F 標題:`_report_findings_missing_severity` 走 `_visible_lines(lines, keep_fenced=False)`,跟拒收偵測用同一份「可見行」實作,圍欄裡的 `## F1` 範例不會被誤判成真 finding——引句:「for no, ln in _visible_lines(lines, keep_fenced=False):」。
- 「多個 F 共用一個 severity」(`## F1` 緊接 `## F2` 才出現 severity):手動 trace 過(未列進正式重現,因為結果符合設計意圖非 bug)——F1 會先被判缺、F2 才吃到那行 severity,這跟規格「每個 F 段都要有自己一行」一致,不是漏洞。
- `scripts/test_lumos.py` 裡這支 patch 新增的 ⑤⑥⑦ 三個案例實際跑過(`python3 scripts/test_lumos.py -k t_report_normalize_flags_finding_without_severity`),7 個子案例全線通過,但都沒有覆蓋到「相鄰 F 段標題層級不一致」這個組合,F1 這個新洞漏測。
