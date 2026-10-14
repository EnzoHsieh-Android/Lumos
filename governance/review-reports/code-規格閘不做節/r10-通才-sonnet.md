severity: minor

## 結論

這輪修補沒有弄壞既有功能。搜尋、門掃描、改用 `_under_root` 的兩處、壞行 fail-closed、門規則版本 8、spec-gate 提示文字都查過,只留一條 minor。

### 驗證方式

- 實驗放在 `/private/tmp/claude-501/-Users-enzo-orca-workspaces-lumos-toolchain-Backend-improve/fe5c4f58-e7fb-477f-be55-0823b5438608/scratchpad/cr-sgn10-通才/`。
- 我把上一輪(`59355e78`)和這一輪(`db8a7c6c`)的 `scripts/lumos` 各取出來,載成模組互相比對。
- 沒有在 spec-gate-nondo 跑寫帳的指令。小子集測試各跑一次:
  - `-k zero_width`:32 過
  - `-k door_rule`:15 過
  - `-k cjk`:36 過
  - `-k nogo`:324 過
  - `-k ledger_physical`:8 過

## finding

severity: minor
blocking: 否 — 只在不同 Python 版本的機器之間才會有不同判定,現行最低 3.14 下沒有實際失敗,作者也已明寫成上限並掛了 REVISIT
引句:「未指派 Cn、私用 Co、代理 Cs、」
問題:看不見字元改按 `unicodedata.category` 判,其中 Cn(未指派)取決於跑這支程式的 Python 的 Unicode 版本。預設可忽略全表另外釘死在 Unicode 16,所以兩個判準的版本不一致。
具體失敗情境:一份計劃的危險詞旁邊有新版 Unicode 才指派的字元,例如 `pay` 加那個字再加 `ment`。
- 在新版 Python 的機器上跑 spec-gate,這個字是已指派的可見字元,不會被刪,判風險低,留痕寫成低。
- 另一台舊版 Python 推送前重判,同一個字是 Cn,被刪掉後 `payment` 命中,判風險高,推送被擋,訊息卻說是「風險低的放行不再成立」。
- 反過來也成立:舊版判高、新版判低,審查的人會在不同機器看到不同結果。
- 作者已在 docstring 第 ④ 點承認這是上限,並掛了 REVISIT:2026-12-31,我只是提醒它會讓留痕在跨版本機器上判定不重現。
佐證:``file: `scripts/lumos:5018` ``(`_INVISIBLE_CATS`)、``file: `scripts/lumos:5058` ``(REVISIT 行)

## 已讀,無 finding

1. **`_is_invisible` 對搜尋的影響**
   - `_cjk_bigrams` 的 `「檢索優化排序」`、`「作廢訂單點數怎麼收回」`、`「が゛ぎ検索優化」` 在兩個版本輸出完全相同。
   - `_cjk_nospace_hint` 的結果也相同。
   - `cmd_search` 的主比對用的是 `nfc(term)`,沒有經過 `_strip_zero_width`。Mn 整類刪除只影響字對回退與提示。
   - 空白字元不刪,所以 `_ANY_SPACE_RE` 的判斷不變。
   - ASCII 快路徑現在會用 translate 拿掉 Cc 控制字元(`\x1c`–`\x1f` 是 isspace,不刪)。呼叫端只拿去做比對,不改寫使用者的文字。

2. **門掃描與既有筆記**
   - 對本 repo `docs/lumos-toolchain-knowledge` 下 879 篇 md,新舊 `_door_keyword_hits` 的命中完全相同(0 篇不同)。沒有既有計劃因為這次改法從低變高。
   - 先刪、NFKC、再刪確實讓 `pay\u0301ment`、`pay\u180bment`、`退\u0000款`、`pay\u2800ment` 和全形夾組合記號的寫法命中。
   - 效能:56 萬字元的純中文,上一輪 0.25 秒,這輪 0.47 秒,可接受。

3. **`cmd_impact` 與 `_cap_retro_check` 改用 `_under_root`**
   - 在 POSIX 上與原寫法等價:相對路徑接 root,絕對路徑照用。
   - 唯一差別是 root 為 None 時,舊寫法會 TypeError,新寫法退成相對路徑,算改善。
   - `t_nogo_shared_helpers_used`(含擴大後的 `os.path.isabs` 檢查)在 `-k nogo` 內通過。

4. **推送前壞行 fail-closed**
   - 用 `_canary_ledger_rows` 實讀兩本帳,都是 0 個壞行:spec-gate-nondo 的 `docs/.canary-log.jsonl` 4543 行,Backend_improve 的 4083 行。沒有本來就讀不懂的行,所以沒有「所有走 -std 的計劃都推不上去」的問題。
   - fail-closed 與 `loop status --disposal` 同一套:帳裡任何壞行都會擋全部 -std,不分是哪個迴圈的。
   - 這是跟 loop status 一致的既有語意,不是新退步。
   - 帳目前沒壞行,所以只是未來有壞行時要先修帳。

5. **完整設計審形狀檢查(`_nogo_full_review_shape`)對既有帳**
   - 帳中非 code- 的 187 個迴圈形狀合格。12 個 -std 迴圈裡有 2 個舊的不合格:`lumos-show讀取入口-std` 沒記分級,`checkt-python-std` 有一筆沒帶輪次。
   - 這個 (b) 出口是這個分支新加的,沒有既有計劃靠它推過,不影響。
   - tier 只由第一筆定錨,加上 loop next 範本會帶 `--tier`,所以正常的 -std 不會誤擋。
   - 整列保留的規則(`_spec_gate_full_row`)也讓 `tier` 欄位在 -std 列裡讀得到。

6. **門規則版本 8 對既有留痕**
   - 帳裡舊留痕的 door_rule 多為 1。版本只用在「較舊/較新」提示文字和 doctor 前 30 份的重數(`scripts/lumos:3259`)。
   - 是否過期仍由重判加 `clause_sha` 決定,版本 bump 不會讓舊留痕自動失效。

7. **治理帳只讀一次(`ctx["gov"]`)**
   - `_cap_retro_status` 傳入 events 時自己會依 loop 篩選,gov_err 的 fail-closed 路徑也維持,語意和不傳時一致。

8. **`_ledger_physical_lines` 改 bytearray**
   - 用 1、2、3、5、7 位元組的區塊,對 3000 組含 `\r`、`\n`、`\r\n` 交界的隨機輸入比對新舊輸出,0 筆不同。
   - 輸出型別都是 `bytes`。30MB 單行 0.14 秒。

9. **spec-gate 提示文字**
   - 所有斷言都只比對前綴或關鍵片語(`PASS(風險低)`、`風險低,但不做清單略過了 1 個危險詞(退款)`),沒有測試或下游依賴舊字。
   - 文件(AGENTS.md、CLAUDE.md、`scripts/templates/graph-discipline.md`、`docs/指令參考.md`)已含新說法。

10. **anchor-baseline**
    - `scripts/test_lumos.py` 的 sha256 與 `governance/anchor-baseline.json` 一致。

最高等級 minor,blocking 0 條。
