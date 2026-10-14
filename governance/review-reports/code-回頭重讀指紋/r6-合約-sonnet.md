severity: minor

這輪修補的主線是對的,我沒找到 major。跳過帳位置的說法和程式一致:`skipped-env` 不在 `_GOV_LOCAL_PAIRS` 白名單,而且實際寫進有進版控的 `docs/.governance-log.jsonl`。新增與改寫的測試都過了:
- `t_reread_fp_timeout_blocks`
- `t_reread_fp_entry_hides_external_diff_from_children`
- `t_reread_fp_mainline_name_edges`
- batch / split / file_replaced / `t_patch_fingerprint_b_in_path_name` 這幾組

兩篇筆記的 `lumos lint` 都是 0 問題。`[closed:…]` 的寫法合格:日期加理由,沒有方括號。以下是還沒收乾淨的小處。

severity: minor
blocking: 否 — 只是歷史摘要行裡殘留舊說法,不影響程式行為與閘
引句:「功能分支的分岔點照實寫成信任本機追蹤 ref」
問題:r5 紀錄說已拿掉「CI 補驗」的說法,但「CI 補驗」沒有全清。計劃筆記 r3 摘要那行(`回頭重讀指紋不因主線前進失效_計劃.md:159`)仍寫「本機偽造遠端追蹤 ref(推主線時核對分岔點、功能分支由 CI 補驗,〈做法〉3、S32)」。這行是這次 patch 沒碰的舊行。它有兩處跟現況矛盾:
- 「CI 補驗」跟第 55 行「CI 只印不擋,不是補驗」互相打架。
- 「核對分岔點」早在 r4 就拿掉了(`_note_reread_bp_vs_remote` 已刪)。
失敗情境:下一個 session 的 AI 用 `lumos search "補驗 CI"` 先撞到這行,以為功能分支偽造追蹤 ref 有 CI 補位,把天花板判成有補償。
佐證:``file: `docs/lumos-toolchain-knowledge/Projects/回頭重讀指紋不因主線前進失效_計劃.md:159` ``

severity: minor
blocking: 否 — 屬寫法與紀錄完整度,不破壞合約
引句:「使用者裁定刻意多步偽造本機 ref 屬範圍外天花板、不加機制」
問題:「CI 只印不擋」是會過期的承認句。鐵則 4 要求把它搬成獨立一行回頭條件,這裡改成直接把 REVISIT 標 closed(計劃第 132 行)。那一行是 `[closed:2026-10-14 …]`,doctor 不會再唸,所以現在沒有任何會到期或被事件觸發的回頭點。「使用者裁定」只出現在散文裡,沒用 `lumos decision-add` 記成 `decisions:` 欄位。依專案 CLAUDE.md,散文不是結構化出處,沒法拿來擋程式或擋之後的翻案。
失敗情境:之後有人看到「CI 只印不擋」想補強,查不到決策紀錄,也沒有 REVISIT 提醒,無從判斷這是已裁定的天花板還是疏漏。
佐證:``file: `docs/lumos-toolchain-knowledge/Projects/回頭重讀指紋不因主線前進失效_計劃.md:132` ``(第 131 行是對應的〈實務隱患〉)

severity: minor
blocking: 否 — 條款與測試對不齊,但測試本身有守住行為
引句:「①b照訊息說的單次跳過 → rc0、印的帳位置照實、skipped-env 記進 docs/.governance-log.jsonl(不是本機帳)」
問題:這條新斷言掛在 S27 底下(`[test: t_reread_fp_timeout_blocks,…]`),但 S27 條款文字(計劃第 111 行)完全沒提「跳過的帳寫在哪一本」,patch 也沒改這條。條款與綁定測試不是一一對上:帳位置的約束只活在〈做法〉5 的散文和測試註解裡。另外 ①b 在斷言前直接讀 `docs/.governance-log.jsonl`,沒有 `is_file` 保護。帳沒寫到那本時會丟 FileNotFoundError,不是乾淨的 check 失敗。
失敗情境:有人把 `skipped-env` 加進本機白名單,測試以例外收場,而不是指出哪句條款被破壞。
佐證:``file: `scripts/test_lumos.py`(patch 內 `t_reread_fp_timeout_blocks` ①b 段)``;``file: `docs/lumos-toolchain-knowledge/Projects/回頭重讀指紋不因主線前進失效_計劃.md:111` ``

severity: minor
blocking: 否 — 只影響沒跑過 init 或寫帳失敗的情境,判定不受影響
引句:「已記進 docs/.governance-log.jsonl:有進版控,跟著帳本提交送出」
問題:單次跳過那條訊息(`scripts/lumos:37745` 附近)先印「已記進 …」,然後才呼叫 `_gate_event_or_warn`。這個函式在沒有治理帳時回 None 而不寫,寫失敗只在 stderr 補一句警告。所以「已記進」在兩種情況下是說早了:
- 專案沒有治理帳(沒跑過 `lumos init`)。
- 寫帳失敗。
這跟 r4、r5 一直在修的「訊息說得比實際強」是同一類。
失敗情境:在沒有 `docs/.governance-log.jsonl` 的消費專案跳過,輸出仍說「已記進 docs/.governance-log.jsonl」,但根本沒有那本帳。
佐證:``file: `scripts/lumos:37745` ``;``file: `scripts/lumos:1622` ``

另外確認過、沒問題的:
- 計劃第 55 行、`Systems/筆記內容審.md`、`Systems/lumos-cli-lifecycle.md`、`06-代碼審與推送.md` 四處的天花板寫法一致,都是「功能分支信任本機追蹤 ref,CI 那一步不帶 `--gate`、只印不擋」。這跟 `ci.yml` 第 247 行起那一步的行為相符。
- `skills/lumos-project-notes/commands/06-代碼審與推送.md` 的帳位置說法也跟程式一致。
- S31、S32、S33 的新測試名都在條款綁定清單裡,沒有懸空。

最高等級 minor,blocking 0 條。
