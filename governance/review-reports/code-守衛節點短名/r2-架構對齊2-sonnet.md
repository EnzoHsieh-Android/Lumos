severity: major

## F1 檔名提醒有兩條收尾線,r2 只補了其中一條,另一條還是會印得像全都乾淨

severity: major
blocking: yes

第二輪第 4 點宣稱要修的是「自檢收尾那行:有檔名提醒時不再印得像全都乾淨」。但 S15 這段其實有兩條收尾的 `ok()`:
一條是 `if not _gover and not _gsoon and not _gover_other:` 分支(全域真的乾淨),另一條是
`elif not _gover and not _gsoon:` 分支(這次沒碰到,但 `_gover_other` 還有別人的債)。這批只改了第一條:

引句:「            ok("沒有逾期或快到期的預告合約" + (f"(但上面有 {len(_gtrunc)} 篇檔名要改)" if _gtrunc else ""))」

第二條(`elif` 那支)完全沒動,還是原樣印「沒事」,而且它自己的註解白紙黑字寫著它才是「唯一」會被誤讀成全乾淨的訊號:

引句:「            # ★這一行是唯一會被當成「全都乾淨」掃過去的訊號★(代碼審 r1 通才席):」

這句註解本身在 r2 之後已經不成立——r2 新增的第一條 `ok()` 現在反而是有修的那條,`elif` 這條才是漏網的那個「唯一」。

實測(在 /tmp 建的臨時 vault,不是本 repo):先用 `guard plan` 建一篇被改名成舊截斷樣式的守衛節點(製造 `_gtrunc`),
再建一篇沒有 `about_code`、日期已過期的守衛節點(製造 `_gover_other`,靠 `doctor --touched-from <空清單>` 讓它落進
「這次沒碰到」那桶而不是 `_gover`),跑 `lumos doctor --touched-from <空清單>`,S15 段尾巴印出:

```
  ⚠ 有 1 篇守衛節點的檔名是舊規則從合約原文截斷出來的(斷在句子中間):
      • Verification/2026-09-23_工作者在副作用與持久結果都已完成-但送出確認前當機時-重新投遞後新的工作者不得再.md
  建議: 改成短名(日期前綴可留可拿掉),連同引用一起改:scripts/graph-rename.sh <舊名> <新名>
  ✓ 這次改動沒碰到任何逾期的預告合約(上面那 1 條還在,只是不擋這次推送)
```

最後一行是 `ok()`(打勾),緊接在檔名提醒下面,完全沒提到上面那 1 篇檔名要改——跟 r1 架構席指出的那個「掃過去」風險是同一個形狀,只是換了一條分支。這是推送前閘(`--touched-from`)實際會走到的路徑,不是罕見組合:任何一次「這次改動沒碰到別人的逾期合約,但這次改動的 repo 裡還有舊截斷檔名」都會踩到。

file: `scripts/lumos:2367`(`elif not _gover and not _gsoon:` 那個 `ok()`)

## 已驗過、判定沒問題的路徑

- **NFC 正規化順序**:`_guard_name_problem` 是先 `n = nfc((name or "").strip())` 再用 `n` 做長度與字元檢查
  (`scripts/lumos:10769-10775`),`_guard_plan_check` 建檔名時也是 `nfc(name.strip())`
  (`scripts/lumos:10833`)——兩處算的是同一個字串,驗證與組檔名用的是同一份正規化結果,不存在「同一個名字
  兩種寫法一個過一個擋」。用 `unittest -k t_guard_plan_requires_short_name` 實跑過,NFD/NFC 兩種寫法都通過、
  存檔一律是 NFC。
- **字元類別常數是否三處等價**:`_GUARD_NAME_CHARS = r"\w一-鿿-"` 被 `_guard_plan_slug`、doctor 的截斷比對、
  `_GUARD_NAME_OK_RE` 三處原樣內插進各自的 `[...]`/`[^...]`,跟改動前各自手寫的字面一致,沒有轉義或範圍上的落差。
- 兩支相關測試 `t_guard_plan_requires_short_name`、`t_doctor_flags_truncated_guard_names` 實跑皆綠
  (`python3 scripts/test_lumos.py -k <名字>`,12 與 10 個子檢查全過)。
