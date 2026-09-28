severity: minor

# 第 4 輪 正確性席(opus)

鏡頭:正確性——預設這段會在某個輸入下壞,找出那個輸入。只審 r4-snapshot.patch(e4158902 → 85d5fada)。

## F1 嚴格模式下,頂端那一版逐篇讀失敗仍當成「沒有翻轉」,轉正事件靜默放行

severity: minor
blocking: 否 — 要在同一棵樹的批次讀剛成功之後,單次 git show 又失敗才會觸發,機率低;但跟「strict=讀不到算判不了」的宣稱不一致
引句:「ty, st = _note_audit_status_of(reader(p))」

1. `_notes_status_flipped` 在 strict=True 時,對每篇候選先用 `reader(p)` 讀頂端那一版(走 `_nodehome_reader` → `_lens_git show tip:p`)。讀失敗回 None → `_note_audit_status_of(None)` 回 (None, None) → `tip_ok` 為假 → `continue`,這篇就從「passed」裡消失。這一處讀失敗沒有照 strict 回 None。
2. 存量漂移這條路的候選 `g_only` 本來就是從同一棵頂端樹(`tenv`)挑出「終點是 pass 的守衛紀錄」,所以這裡的 `reader(p)` 是多讀一次;它一失敗,c1 就從「要處理」掉到什麼都沒有,`unknown` 也是空的,block 模式照樣回 0。
3. 重現(把頂端逐篇讀換成失敗,其他全用真 git):
   `python3 /private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/cr4/p4/repro_reader.py`
   輸出:
   `正常:must 4 unknown []`
   `頂端逐篇讀失敗:must 0 unknown []`
4. 同一族的其他讀取(批次讀、改名對照、起點那一版)這輪都照 strict 改成回 None,只剩這一處。修法可以是 strict 時 `reader(p)` 回 None 就回 None,或存量漂移這條路既然已經有 `only`,就跳過這次重讀。
file: `scripts/lumos:24515`

## F2 樹上讀不出來的筆記現在找得到,考試重放碰到它會丟例外(上一版不會)

severity: minor
blocking: 否 — 只有離線的考試指令會中,而且要考題的 status_targets 剛好指到一篇不是 UTF-8 的計劃
引句:「return Env.from_texts(Path(root) / vault_rel, texts, unreadable=[b for b in bad if b not in (override or {})])」

1. 這輪把解不開的筆記用空欄位的 Note 放進 `tenv.notes`(r3 之前是完全不進 notes)。所以 `tenv0.resolve(...)` 現在會解到它,但 `env_text(tenv0, prel)` 仍回 None(`_texts` 裡沒有它)。
2. `_drift_exam_replay` 對每個 status_target 直接呼叫 `_drift_set_status_text(env_text(tenv0, prel), "done")`,裡面第一行是 `text.split("\n")` → 丟 AttributeError,整支 `drift exam` 中斷,也沒有「略過」的判讀。
3. 重現:
   `python3 /private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/cr4/p4/repro_exam.py`(一篇 Projects/壞.md 內容含 \xff,target `[[Projects/壞]]`)
   本版:`例外: AttributeError 'NoneType' object has no attribute 'split'`;同一支腳本改載 e4158902 版:`回傳: set()`。
4. 另外查過其他會從 tenv 解連結再讀全文的地方:c5 的家筆記(`htext is not None` 有擋)、c2/c4(`or ""` 有擋)都沒事,只有考試重放這一處沒擋。
file: `scripts/lumos:25895`

## F3 doctor 開關提醒的新條件,跟函式說明和計劃 [S14] 對不上

severity: minor
blocking: 否 — 文件跟程式不一致,行為本身已經寫進 Systems 筆記「跟設計稿不一樣」那一節
引句:「開關不是 block 就講(不管接線沒,設計 [S14])」

1. 這輪把條件收成 `mode != "block" and (wired or _drift_gate_explicit(txt))`:沒接線、也沒寫設定時不印。可是同一支函式的說明第一句還寫著「不管接線沒」就講。
2. 計劃這輪只改了 [S2],[S14] 跟〈做法〉那句「gate 不是 block 時 doctor 印一行」都沒改。沒接線也沒寫設定的專案,照條款應該印一行,程式不印;綁的測試 t_doctor_drift_section 仍是綠的,所以這個落差測試抓不到。
3. 附帶一點:接線了但沒寫設定時,印出的句子是「(.lumos/config.json 的 drift_check.gate)」,原本那句「沒寫就是預設」被拿掉了,讀的人會以為自己寫過這個開關。
file: `scripts/lumos:25804`
file: `docs/lumos-toolchain-knowledge/Projects/存量漂移防線_計劃.md:144`

## 已看、無 finding 的部分

- `_guard_formal_line` 改用 INV_TAG_RE 與 invariant_test_refs:已看,無 finding。用小探針逐一跑過(`cr4/p4/probe1.py`):`[test:ios:t_refund]`、`[test: t_a , t_refund ]` 認得;`[test:t_refund_v2]`、`[test:Pay.t_refund]` 不認(比完整名,沒有子字串誤中);合約原文結尾的 `[keeps]`、`[manual:…]` 會剝掉,原文結尾的 `[scope:…]` 不剝(r2 釘仍綠)。合約原文本身帶 `[test:x]`/`[src:x]` 時,兩邊用同一支規則剝,比得到;原文帶 `[src:]` 跟沒帶的另一條會被當成同一條,這跟 guard 家族既有的「只差指針就算同一條」一致,不另列。method 經 IDENT_RE 驗過、不會含冒號,所以用「結尾是 `:`+方法名」認平台前綴很安全。
- settle 各分支改用 `_guard_planned_idx`:已看,無 finding。0 條、1 條、好幾條三種情形都走到對的分支;做到一半、正式行已在、預告行也還在的情形,都用 `hlines` 與索引刪行,跟原本的 `_guard_planned_line` 結果一樣。只剝行尾 `[watch:][due:]` 那一對的規矩保留(guard-kill 的 PITFALL,t_guard_claim_with_bracket_tags_still_settles 綠)。
- strict 的傳遞:已看,無 finding(F1 那處除外)。`_drift_range_events` 兩次呼叫都帶 `strict=True`,`_note_audit_closed_plans` 沒帶。不嚴格時的行為我拿 3ba5eef5 原始版逐行對過:歷史讀失敗 → 當成讀不到;起點讀失敗 → 起點狀態當 None;改名對照失敗 → 沿用新路徑。三種都跟原版一致,「照舊」這個說法成立。
- `_note_base_status` 的回傳:已看,無 finding。回 None 只有兩種情形:過了預算,或 strict 時讀不到。不嚴格時回 `(None,)`,呼叫端用 `got[0]`,跟原版把 `base_state` 設成 None 等價。
- c3 每一項都要有落點:已看,無 finding。對過 build_typed_index 的回傳形狀:ghosts 是 `(src, 字面, 種類)`、ambiguous 是 `(src, 字面, 種類, 候選)`、scalars 是 `(src, 種類, 值)`,索引位置都對。plan_refs 寫成區塊文字時整欄不進索引,`plans` 是空的 → 不列,方向是保守的。
- Env.from_texts 的 unreadable 與 stem:已看,除了 F2 無 finding。stem 的切法跟 load_vault 的 `p.stem` 一致(傳進來的一定是 .md 結尾);排序照路徑逐層排,不變;蓋過用的內容(override)裡有的路徑不會被標成讀不出來。
- doctor 開關提醒的條件:除了 F3 無 finding。`_drift_gate_explicit` 碰到 None、壞 JSON、BOM 都回 False,跟 `_drift_config` 的預設一致。
- scan 不寫治理帳:已看,無 finding(治理帳那次呼叫已拿掉,r3 釘 ⑦ 綠)。

## 圖譜鏡頭(這次改動牽連的筆記)

- Systems/guard-kill:不影響。「只剝行尾那一對 `[watch:][due:]`」那條 PITFALL 仍由 `_guard_planned_idx` 的 `_PLANNED_TAIL_RE` 守著;三支指令拿寫入鎖、做到一半可補完兩件事,相關測試都綠(guard_settle 28、guard_commands_hold 4、guard_claim_with_bracket 4,全過)。
- Systems/筆記內容審:不影響它宣稱的行為。新 WHY 說「筆記內容審照舊把讀不到當成沒有翻轉」,我對過原始碼成立。精確一點說:起點讀不到時會當成「這次收尾」,多做一次完成審。這在原版就是這樣,方向偏嚴,不另列。
- Systems/存量漂移守衛:PITFALL 說「預算在每一次 git 呼叫前都看」,我逐一核過,成立。WHY 說「讀不到算判不了只給存量漂移這條路」,但這條路還有 F1 那一處讀取沒做到。
- Systems/lumos-cli-read(d1 讀指令不寫帳):scan 已經改成跟這條一致。
- Projects/存量漂移防線_計劃:[S2] 已經跟程式一致;[S14] 還沒跟上(F3)。

相關測試子集(drift_code_review 44、drift_unknown 1、doctor_drift_section 2、doctor_summary_admits 6)在凍結版上全綠。

最嚴重為 minor,blocking 共 0 條。
