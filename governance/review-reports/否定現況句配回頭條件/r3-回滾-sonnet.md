severity: major

## F1 消費專案的 doctor Check D 不會報紀律區塊漂移,更新提示與回退後的偵測靠的是另一條路徑,spec 沒接上
severity: major
blocking: 是
引句:「**所有消費專案**要下次 `lumos update` 才拿到,在那之前 doctor Check D 會對它們報紀律區塊漂移——發佈說明要寫。」
file: `scripts/lumos:2802`
1. Check D 拿「該 repo 自己的 `scripts/templates/graph-discipline.md`」跟「該 repo 自己的 CLAUDE.md / AGENTS.md 注入區塊」比(`_expected_claude_body(repo_root, …)` 讀的是 `repo_root/scripts/templates/`,即 scripts/lumos 2802 行)。消費專案的這份範本是 `lumos update` 時 vendor 進來的(`_VENDORED_TREE_FILES` 含 `scripts/templates/graph-discipline.md`,`_vendor_toolchain` 先 copy2 範本、再 `_reinject_all`)。
2. 所以消費專案在「工具鏈已改範本、自己還沒 update」的那段時間:本機範本與區塊同為舊版,Check D 比對一致、不報漂移、不擋、也沒有任何訊息。〈做法〉6 與〈影響〉「下次 `lumos update` 之前 doctor 報漂移」這個承諾對消費專案不成立;只有工具鏈自己(範本已改、區塊還沒重注入)會報。
3. 真正會提醒消費專案落後的是 `_version_nudge`(scripts/lumos:17706):比對 CLAUDE.md sentinel 的版本戳與來源 clone 的 `LUMOS_VERSION`(現為 `"v1.0"`,「release 手動 bump」,scripts/lumos:270)。spec 全文沒提要不要 bump `LUMOS_VERSION`;不 bump 則版本戳相同、nudge 靜默,消費專案完全不知道要 update,而發佈說明是唯一通道。
4. 〈回退〉同理:已 update 過的消費專案,本機範本與區塊都是新版,回退工具鏈後 Check D 一致、不報;`_version_nudge` 又是「CLAUDE 版本 ≥ 來源就不提示」,回退不會降版本號。〈回退〉寫的「回退後 doctor Check D 會報紀律區塊漂移,要各自再跑一次 `lumos update`」不會發生:消費專案會靜默留在新鐵則 4(指向 `REVISIT:[when-file:` 寫法、且鼓勵寫條件式 REVISIT,而回退後的工具沒有那道提醒),沒有任何機械訊號叫它們 update 回去。
5. 要改的方向:把偵測通道改寫成實際存在的那條(`LUMOS_VERSION` bump + `_version_nudge`,並註明回退時版本要再 bump 一次才提示得到),或明說「消費專案沒有機械提示,只靠發佈說明」;再補一支測試釘住,不然〈做法〉6 與〈回退〉的期望是假的。

## 已讀,無 finding

- doctor 體積提示線與回退的關係:已讀,無 finding(僅在工具鏈自身,不屬消費專案)。

- 舊版工具讀到新的 `hinted` 事件:已讀,無 finding。實測讀碼:`gov` 的 mapper(scripts/lumos:7277 起)對未知 kind 只原樣帶過,去重鍵含 `check`;`gov --stats` 的「閘的動作」只算 blocked/skipped/fail-open,`_render_gov_nags` 只看 warned;`_KNOWN_GATES` 已含 note-shape;`extra` 的鍵(check/total/hints/truncated)不與 `_gate_event_build` 自己的欄位撞名。舊版讀 `.lumos/config.json` 的 `note_shape.negation` 也只讀 `gate` 鍵、忽略未知鍵(`_note_shape_config`),相容。

- `note_shape.negation` 子開關相容:已讀,無 finding(重複印「note_shape 不是物件」兩句屬 minor,理由:只是雙訊息、不影響判定,放行)。

最高等級:major;blocking 共 1 條
