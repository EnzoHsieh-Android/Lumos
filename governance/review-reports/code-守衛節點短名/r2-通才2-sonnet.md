severity: major

## F1 doctor 收尾行只修了一半:「有 _gover_other 又有截斷檔名」這個組合,收尾那行照樣不提檔名提醒

severity: major
blocking: no

r2 item 4 宣稱「自檢收尾那行:有檔名提醒時不再印得像全都乾淨」,但 patch 只改了 `if not _gover and not _gsoon and not _gover_other:` 這個分支,沒有同步改 `elif not _gover and not _gsoon:` 這個分支(後者對應「這次沒碰到任何逾期,但別人還有逾期在別處」的情境)。兩個分支結構完全對稱、都是唯一的收尾 `ok()` 訊號,r1 通才席當初點名警告的正是後面這個 elif 分支(註解都留著:「★這一行是唯一會被當成「全都乾淨」掃過去的訊號★」),結果 r2 只補了前一個分支。

引句:「ok("沒有逾期或快到期的預告合約" + (f"(但上面有 {len(_gtrunc)} 篇檔名要改)" if _gtrunc else ""))」
引句:「ok(f"這次改動沒碰到任何逾期的預告合約(上面那 {len(_gover_other)} 條還在,只是不擋這次推送)")」

第二條(elif 分支)在 patch 裡沒有 +/- 標記,是原封不動留著的既有行,r2 沒有替它加上 `_gtrunc` 提醒。

**實際跑出來驗證**(用 `/tmp/lumos-r2-test-vault` 之外另建的臨時 vault,呼叫 `python3 /Users/enzo/harness/lumos-toolchain/scripts/lumos --vault <tmp> guard plan ...` 與 `doctor --ci --touched-from`):

情境:①一篇守衛節點檔名是舊規則截斷出來的(觸發 `_gtrunc`)、②另一篇守衛節點已逾期但這次改動沒碰到它管的檔(進 `_gover_other`,不進 `_gover`)、③沒有 `_gover`、沒有 `_gsoon`。這組合完全合法且不罕見(截斷檔名的舊帳跟別人的逾期預告本來就常常同時存在)。

跑出來的 S15 段落收尾:
```
  ⚠ 另有 1 條逾期的預告合約,但這次改動沒碰到它們(不擋這次推送):
      ...
  ⚠ 有 1 篇守衛節點的檔名是舊規則從合約原文截斷出來的(斷在句子中間):
      ...
  ✓ 這次改動沒碰到任何逾期的預告合約(上面那 1 條還在,只是不擋這次推送)
```
最後那行 ✓ 完全沒提到上面那 1 篇檔名要改的提醒,跟 r2 item 4「有檔名提醒時不再印得像全都乾淨」的宣稱不一致——這正是同一段收尾行、同一種「掃過去以為沒事」的形狀,只是換了一個分支。

file: `scripts/lumos:2367`(`elif not _gover and not _gsoon:` 那個分支,未帶 `_gtrunc` 提醒)
file: `scripts/test_lumos.py:4823`(`t_guard_overdue_tail_line_matches_the_list`,只驗證這個分支「不再說沒有逾期」,沒有同時佈置 `_gtrunc` 場景,沒有蓋到這個組合,所以測試套件目前不會抓到)

影響:不擋推送、不影響資料正確性,只是自檢收尾訊息不完整,跟 r2 自己宣稱要修好的問題屬於同一形狀但漏了一半,所以標 major/不擋。

---

## 已驗過、判定沒問題的部份(「重點攻擊」提示的方向)

1. **NFC 正規化的順序跟「組檔名」是否一致**:`_guard_name_problem` 內 `n = nfc((name or "").strip())`,驗證長度與字元都用這個 `n`;`_guard_plan_check` 組 `gname` 時另外呼叫 `nfc(name.strip())`——兩處都是「先 strip 再 nfc」,且輸入同一個不可變的 `name` 字串,兩次呼叫結果逐位元組相同。實際跑:用 `café`×6(NFC 24 字、NFD 30 codepoints)當 `--name`,NFD 寫法在驗證與存檔都用 NFC 後的 24 字計長度,順利建立,沒有「同一個名字兩種寫法一種過一種擋」的情形——因為兩處判定用的是同一份正規化結果,是一致的,不是各算各的。
   驗證指令:`python3 scripts/lumos --vault /tmp/lumos-r2-test-vault guard plan Systems/Pay "NFD邊界測試合約" --plan Projects/退款_計劃 --phase P1 --due 2099-12-31 --why 測試 --owner enzo --name "$(python3 -c "import unicodedata as ud;print(ud.normalize('NFD','café'*6))")"` → 成功建檔 `2026-09-23_cafécafécafécafécafécafé.md`(exit 0)。
   另外實跑 patch 自帶的 `t_guard_plan_requires_short_name`(含新增的 ⑥⑦ 兩段)與 `t_doctor_flags_truncated_guard_names`(含新增的 ⑤⑥ 兩段),全部通過。

2. **字元類別常數在三處是否真的等價**:`_GUARD_NAME_CHARS = r"\w一-鿿-"` 分別餵進 `[^{...}]`(doctor 的 `_gfull`、`_guard_plan_slug`)與 `[{...}]`(`_GUARD_NAME_OK_RE`)。用 8172 個字元(ASCII 全範圍、中文、café 的各種組合形式、控制字元)逐一比對 `neg.match(c)` 與 `pos.match(c)`,結果完全互補、零不一致——三處確實是同一份規則的正反兩面,不是各自維護一份悄悄不同步的字面。

## 沒有繼續往下查的部份
- `_guard_plan_slug` 內對 `_GUARD_NAME_CHARS` 的參照在檔案裡的定義順序(function 在前、常數在後):確認過 Python 模組級名稱是在呼叫時才解析,執行到 `run_doctor`/`_guard_plan_slug` 真正被呼叫時模組早已載入完畢,不是 bug。
- doctor 判斷截斷檔名時,`_gc`(合約原文,從檔案內文直接 read_text 取得)沒有先 `nfc()` 就丟進 `_guard_plan_slug`,理論上如果合約原文含分解形式(NFD)的拉丁重音字元,`_guard_plan_slug(_gc)` 算出來的 slug 可能跟已正規化的 `_gstem` 對不上,讓截斷檔名判定漏抓。但這段程式碼(有沒有 nfc)在 r1 就已經是這樣,r2 只是把字面正則換成常數引用,沒有改這裡的正規化與否——不是 r2 這輪引進的改動,所以沒有另外提報。
