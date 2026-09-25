severity: minor

## F1 空字串日期的防呆只補了 created/updated/date,decisions 的 decided/ended 沒補到,還是會被空字串繞過

這輪的 PITFALL 說法是「日期寫成空字串會繞過日期規則與既有的建立日切點,寫了卻空一律報錯」,但實際只在 `_lint_new_rules` 裡對 `_NOTE_DATE_FIELDS = ("created", "updated", "date")` 這三個頂層欄位加了空字串防呆:

引句:「if k in n.fields and (v is None or str(v).strip() == ""):」

decisions 陣列裡的 `decided`/`ended` 還是走舊邏輯,遇到空字串會被 `str(v).strip() != ""` 那個條件直接跳過、不判:

引句:「if v is not None and str(v).strip() != "" and not _note_date_ok(str(v)):」

翻紅重現:在 /tmp/lc-r2(clone 自本 repo、套上這份 r2 patch)起一個開關 on 的 vault,寫一篇筆記:

```
decisions:
  - content: 測試決策
    id: d1
    decided: ""
    valid: true
```

跑 `python3 scripts/lumos --vault <vault>/kg lint 決策空日期`,只會報「沒寫 aliases」,`decided: ""` 完全沒被抓到——跟同一輪對 `created: ""` 的處理(會報「created 寫了卻是空的」)不一致。`decided` 是「翻案時序比對」(第 i 條 decisions 的 `decided`/`ended` 排序決策先後)實際會讀的欄位,空字串一樣會悄悄套錯規則,跟 PITFALL 描述的風險是同一種,只是這輪沒把它一起補。

這段 decisions 迴圈本身不是這份 r2 patch 改到的行(diff 裡沒有 + 號),所以嚴格說是延續第一輪就有的舊洞、不是這輪新引入的迴歸;但這輪的 PITFALL 敘述讀起來像是「日期空字串」這類問題已經一次補完,實際上範圍只到頂層三個欄位,容易讓人誤以為 decisions 也覆蓋到了。

severity: minor
blocking: no

## 已驗過、沒問題的路徑

- `type` 寫成清單/字典/數字時的防呆:在 /tmp/lc-r2 起的 vault 裡把一篇筆記的 `type:` 寫成兩行清單(`- system` / `- issue`),`lumos lint` 與 `lumos doctor --ci` 都沒有 Traceback,各自把它列成該篇的一條 error,行為跟 t_doctor_note_lint_survives_malformed_note 期望的一致。引句:「errs.append(f"type 要是一個字串(一篇只有一種類型),你寫的是 {type(t).__name__}——改成 type: <類型>")」
- S6 總索引段對非字串 `type` 的 isinstance 防呆(統計數與跳過邏輯都補齊,兩處 `n.fields.get('type') in _scope` 都加了 isinstance 檢查),沒有另外漏掉的第三處用法。
- `.lumos/config.json` 整份不是物件(空檔案觸發 JSONDecodeError、和 `null`/陣列/純量)都會落入警告分支、用預設 warn,不會悄悄吃掉也不會擋下——實測空檔案(`: > .lumos/config.json`)輸出「.lumos/config.json 讀不了(JSONDecodeError)」。
- `_vault_repo_root` 從 `_repo_root_from_env` 換成往上找 `.git` 之後,`cmd_lint` 與 doctor 的 L 段兩處呼叫點用的是同一支函式、同一份設定,沒有殘留新舊兩套根判斷並存的縫。
- 日期帶時間(`created: 2026-09-25 10:30`)這種「非空但格式錯」的輸入照樣被 `_note_date_ok` 擋下、不會被空字串防呆誤放行,兩條防呆彼此不衝突。
