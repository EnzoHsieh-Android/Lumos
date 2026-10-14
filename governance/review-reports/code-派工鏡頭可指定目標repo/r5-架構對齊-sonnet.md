severity: minor

整體判定:這一輪沒有引入第二種做法,也沒有跨層直呼。有兩條 minor,都不擋。

## Findings

severity: minor
blocking: 否 — 只是多一層薄轉手,沒有第二套消毒規則,屬風格層級
引句:「def _lens_author_names_show(names, limit):」
對照:`_lens_author_names_show` 在 `scripts/lumos` 全檔只被 `_lens_spec_names_line` 呼叫(`scripts/lumos:49213`、`scripts/lumos:49222`)。其中的白名單判斷都落在單一出口 `_lens_author_name_show`。
判定理由:包裝有 2 層(`names_show`、`names_line`),其實一支就夠。但兩支都靠 `t_dispatch_lens_spec_author_names_single_exit` 的 `_LR4_EXIT` 守住本體必呼叫出口,不會長出另一套規則。這是多一層,不是多一種。
佐證:``scripts/test_lumos.py: `scripts/test_lumos.py:44664` ``

severity: minor
blocking: 否 — 守衛形式與既有「掛鉤複本」慣例不完全同形,但有補償,不是第二套機制
引句:「SPEC_NAME_MAX = 300」
對照:既有的 hook 複本守衛是整段或語法樹逐字比對,而且掃全部 hook,不寫死清單。例如逾時預算那段 `scripts/test_lumos.py:17964`、`_ci_latest_attempts` 的語法樹比對 `scripts/test_lumos.py:28718`、注入框整段 `scripts/test_lumos.py:17814`。新的 `t_dispatch_lens_hook_name_rule_matches_lumos`(`scripts/test_lumos.py:44623`)只比四個常數,而且只載入 `dispatch-lens-hook.py` 一支。
判定理由:
- 這兩份判斷函式(掛鉤的 `_spec_name_show` 與 lumos 的 `_lens_author_name_ok`)結構本來就不同:lumos 那份呼叫 `_path_special_chars`,掛鉤那份內聯類別迴圈。所以做不到語法樹逐字比對,改成比常數是合理的。
- 掛鉤抄常數、加比對測試,這件事本身跟專案既有做法一致。
- 殘餘落差:判斷邏輯本身(長度下限、`fullmatch`、類別 any)沒有比對守衛,只靠行為測試 `_lr_hook_fire` 那組句子。若日後嫌這裡不夠,可以把比對改成把兩邊對同一批樣本跑一遍。這不是現在的 blocker。
佐證:``scripts/hooks/claude/dispatch-lens-hook.py: `scripts/hooks/claude/dispatch-lens-hook.py:60` ``

## 點名項目的結論

- ① 單一出口與兩支薄包裝,是收斂不是新增。
  - 這一輪把前幾輪散在 `_lens_spec_charset_ok`、`_lens_spec_path_showable`、`_lens_spec_name_ok` 的三條白名單判斷收成一個出口 `_lens_author_name_show`,同時刪掉了兩支舊函式。
  - 與既有消毒的關係分工清楚:
    - `_lens_visible`(`scripts/lumos:17174`)仍是 `out["text"]` 的最後一道,把控制字元轉成 `\uXXXX`(`scripts/lumos:49799`)。
    - `_kill_esc`(`scripts/lumos:17180`)是它的底層。
    - `_esc_clean`(`scripts/lumos:12328`)是逃逸帳專用的有損清洗,docstring 明說不併。
    - `_plain_label` 是注入框的標籤清理。
  - 新出口是「白名單不合就換成固定字樣」,用在作者可寫的名字上。它跟「逐字跳脫」是兩種語意,但疊在 `_lens_visible` 之前,沒有取代它。
  - 這個疊法在 r3 就已存在,這輪沒有新增第三種。
- ② `_path_special_chars` 加 `extra` 是沿用。
  - 該函式的 docstring 早就寫著「各處自己決定,用參數表達,不另抄一組」,`surrogate` 參數是同一個形狀。
  - `extra` 讓名字白名單不必再寫自己的類別迴圈。調用處只有 `scripts/lumos:49202` 一個。預設值 `frozenset()` 不改既有 13 處呼叫的行為。
  - 已讀,無 finding。
- ③ 掛鉤抄常數加比對測試:見上面第二條 minor。
- ④ AST 守衛測試與既有結構守衛同形。
  - 同樣是 `ast.parse` 加 `ast.walk`、預設不准,另有「前置:變異點在原始碼裡」與「守衛抓得到」的成對變異檢查。
  - 同樣把豁免寫成逐條附理由的表(`_LR4_NOT_OUTPUT`、`_LR4_SAFE_EXPRS`),形狀與 `_NOT_LUMOS_PROGRAMS`(`scripts/test_lumos.py:8403`)那類相同。
  - 掛鉤端的 `t_dispatch_lens_hook_spec_what_single_exit` 用同樣的寫法,守 `.format(what=…)`。
  - 已讀,無 finding。

## 其他已讀範圍

- NFC 去重(`_lens_spec_code_cands`、`_lens_spec_linked`、`_dispatch_lens_spec_arch_text`)三處寫法一致,而且沿用 `_nodehome_landing_missing` 既有的 NFC 鍵比對慣例。已讀,無 finding。
- 掛鉤的 `_range_what` 把三個說明行的重複判斷收成一支。`_clean_field` 仍只用於 repo 路徑,沒有新增第二條路。已讀,無 finding。

最高等級 minor,blocking 0 條。
