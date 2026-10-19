preflight-4: ran

# r1 前掃收貨(編排者派的便宜 agent 掃四類;作者照結果修真檔)

## ① 未定義的詞(3 處,直接修真檔,不算 findings)

1. 〈依據〉用 F8、B6、W8、F17、W9、B1/B11 等編號指向「web 示範比對表」,沒有出處。前掃建議指向 [[Projects/Web示範前端缺口_調研]];這個工作樹沒有那一篇(`ls docs/lumos-toolchain-knowledge/Projects/` 查無),所以改成:〈依據〉講明比對表是編排者的清單、不在圖譜,並新增〈名詞〉一節把每個編號逐一寫成一句白話。編號保留,方便跟比對表與其他席位對照。
2. 「S15」一字兩義:§9 B8 寫「S15 的 nudge」(是 home check 的家提醒,原出處是每支檔有家計劃的條款號),跟本篇驗收條款 [S15] 撞名。改成「`home check` 的家提醒,程式裡叫 nudge」;同節的「S13、S13b」改成明寫是 [[Projects/每支檔有家_計劃]] 的條款。〈名詞〉另列 doctor 段名 P、S8、S9、S10、S14 各一句說明,並註明 S13、S13b 不是本篇條款、也不是健檢段名。
3. 審查帳、治理帳、本機帳:〈名詞〉寫出各是哪個檔(審查帳=docs/.canary-log.jsonl,消費專案裡被 init 產的 .gitignore 忽略、即本機帳;治理帳=docs/.governance-log.jsonl,進版控)。

## ② 壞引用(2 處,直接修真檔)

1. §8 寫 `_node_code_ref_tokens(..., cmdline=True)`,現行函式沒有 cmdline 參數 → 改成「要替 `_node_code_ref_tokens` 新增一個 `cmdline` 參數(現在沒有)」。
2. §1 第 7 點說頂層指令數在 ARCHITECTURE.md 有兩處;實際寫 91 的是 ARCHITECTURE.md 第 3 節標題、同節圖的根節點、同節結尾那句共三處,另 skills/lumos-project-notes/reference.md 兩處(子命令全覽、介紹 commands/INDEX.md 那句) → 改正,並寫明 `t_docs_command_count` 掃全部活文件。
3. 作者修完自跑 refcheck 時另抓到一處:〈名詞〉新寫的 `docs/.gitignore` 在工具鏈 repo 不存在(那是消費專案 init 產的)→ 改成不加反引號的描述。refcheck 0 missing。

## ③ 範圍自相矛盾:0 條

## ④ 機械宣稱驗語意(1 處,修真檔;沒動核心裁定節)

§1 第 4 點(summary-add 寫前形狀檢查)在不是 git 專案時的行為。

- 修改前:「不是 git 專案時這兩道照 `_drift_fix_shape_err` 原本的行為講一句、跳過。」
- 現況(讀碼):`_drift_fix_shape_err` 在 `_nodehome_list(root, "index")` 回 None 時回錯誤字串「git 列不出檔案清單,沒辦法先跑筆記形狀擋」;唯一呼叫端(drift fix 的寫入流程)把非 None 當擋下、rc2。所以現況是擋,不是跳過。
- 修改後:「不是 git 專案(或 git 列不出檔案清單)時照 `_drift_fix_shape_err` 現在的行為:它回錯誤字串、呼叫端當擋下,summary-add 同樣 rc2 不寫並印那句原因——不另寫跳過分支(圖譜本來就在 git 專案裡、提交前掛鉤也要 git,單人使用不值得多一條路;跟 `drift fix` 同一個擋法)。」
- 判:選「擋」。理由一行:不過度設計,跟既有寫入工具同一個擋法,不多開一條沒有提交檢查保護的寫入路。
- 是否動到核心裁定:否。決策 d1 只說「寫入前跑提交時同一套檢查」,這次只把「跑不了時怎麼辦」照現況寫對,沒改 d1、d2,不升成正式 finding。

## 未驗項:作者自己追

W5「整串指令當路徑」在 doctor P 段:讀碼(cmd_doctor 的 P 段自己抽反引號,只剝 `:行號` 尾巴,不切空白,整串 `exists()`)並實跑確認。2026-10-15 在暫存目錄造一個 git repo:有 scripts/e2e.sh、e2e/.gitignore 忽略 .run-state,一篇 Systems 節點寫 `scripts/e2e.sh --cleanup` 與 `e2e/.run-state`,跑 `lumos doctor`:

```
[P] 筆記提到的程式檔路徑,檔案還在不在(提醒,不擋)
  ⚠ 有 2 處筆記提到的程式檔路徑已經不存在(碼被刪或搬了?):
      • Systems/A.md → scripts/e2e.sh --cleanup(已不存在)
      • Systems/A.md → e2e/.run-state(已不存在)
```

HIT:兩項都重現(指令加參數、被忽略的執行期檔),計劃 §8 的描述成立,不用改。暫存 repo 已刪。

## 六席收貨與處置(2026-10-15)

收貨:正確性 8 條(major 4)、邊界 7 條(major 2)、整合 6 條(全 minor)、資源併發 3 條(major 1)、回滾 3 條(major 2)、架構對齊 5 條(major 1)。共 32 條,major 10、minor 22;blocking 10(正1–正4、邊1、邊2、資1、回1、回2、架1)。全部折入,駁回 0 條。

四類:①未定義的詞 2 條(正8、邊6:開頭編號數)②壞引用與落點 4 條(整2、整3、整6、架5)③範圍或說法自相矛盾 3 條(整4、整5、回3)④語意不成立 23 條(其餘)。

| 根因組 | 條目 | 折法 |
|---|---|---|
| (a) 改舊行被當新寫 | 正1、邊3 | §1 第 4、6 點:格子檢查的「舊行鍵」照提交時的來源組(HEAD 版本這篇摘要的每一行,summary-line 另加被換掉的那一行),禁止傳 None;S7 補改舊行放行 |
| (b) 沒前綴的行繞過檢查 | 正2 | §1 第 1 點:新行要以 SYMBOL_RE 認得的前綴開頭,否則 rc2;S3 補 |
| (c) 實作後補跑的步驟 | 正3、邊界序言 | 實測見下表;§10 B1(b) 改成:先提交 → 既有檔用 git restore 換回 → 新檔換成空殼、不要移走(移走是匯入失敗、弱證據)→ 都做不到改 plan_risk: high;S25 改 |
| (d) F29 判法與成本 | 正4、正5、資1 | §5:一行整組判,有一個判不了或不成立就不唸;比對基準改上游追蹤分支、沒有才 HEAD,漏唸寫成天花板加 REVISIT;沒有條件就不呼叫 git、索引清單整次執行讀一次;S13、S14 改,補 S32 |
| (e) 條件開頭詞子字串誤吞 | 正7、邊2 | §4 記號 3:只認段首,先比既有 `_TRIGGER_STOPWORDS`(若干、若是…),拿掉這時、此時;〈不做〉補一句;S11 補兩句應照列 |
| (f) 列檔與忽略檢查的邊角 | 邊1、邊5、資2、資3、架4 | §9 W6:走 `_nodehome_git` 帶 -z、限 `-- <圖譜>/Systems`、NFC 還原、已刪檔略過;§8:忽略檢查走 `_lens_git` 參數形式、先剔除絕對與含 .. 的路徑、rc 不是 0/1 就整步判不了;S23 補、補 S35 |
| (g) B3 治理帳的寫讀 | 架1、架2、正6、邊7、整6 | §10 B3:寫用 `_gate_event(..., extra=…)` 平的事件形狀;讀用 `_gov_vc_gate_events` 照 `_nogo_ctx_gov` 第一次才讀、fail-closed;有要跑全套的候選就兩本帳都讀、同計劃取 ts 最晚、token 去重(不再「找不到才讀」);多機寫進實務隱患;補 S33 釘既有讀者不受影響;S28 改 |
| (h) B2 done 計劃 | 回1、整4 | §10 B2:真正改 `_spec_gate_push_scan` 的 full 條件;指紋對不上與測試找不到只提醒不擋,真紅才擋;記決策 d3,[[Projects/雙向門放行_計劃]] 正文補一句指過來;S27 改 |
| (i) 回退 | 回2、回3 | 〈回退〉:LUMOS_VERSION 還原時只能再往前 bump;⑤ 還原後「(新增)」標記會讓舊 refcheck 列 missing;§1 第 7 點同步補一句 |
| (j) 文件與同步 | 整1、整2、整3、整5、邊4、架3、架5、正8、邊6 | B11 同時改 S12 段;守衛補認「N 個指令的總目錄」(S34);寫入指令列舉補 reference.md、README.md、Systems/lumos-cli-write;doctor 段名一律寫「S8 段」並在〈名詞〉說明;lint 已排除行跳過引用塊、只認緊接冒號的;F14 用 `link_target`;lands_in 補 Systems/loop-convergence-recording、Systems/reversibility-governance-ledger;開頭編號數改成 20 |

(c) 兩席相反的機械重現(2026-10-15,/tmp/lumos-plan-web-notes/c,git 2.39.2):

| 編號 | 指令 | 輸出 | 判 |
|---|---|---|---|
| 正3 | 新檔 new.js 已提交、實作前提交沒有它:`git restore --source=<實作前> -- new.js` | rc=0,工作目錄 new.js 被刪(`D new.js`) | 正3 說的 rc1 在這個前提下 MISS |
| 正3 | 新檔 un.js 沒被追蹤:`git restore --source=<實作前> -- un.js` | `error: pathspec 'un.js' did not match any file(s) known to git`,rc=1 | 正3 說的 rc1 在這個前提下 HIT |
| 邊界序言 | 同第一列 | rc=0、等於移除 | HIT |

裁定:兩席各對一半,差在檔有沒有先提交。計劃步驟本來要求先提交,所以 restore 不會報錯,但會把新檔整支移走;正3 後半(移走後測試匯入失敗=跑不起來=弱證據,不算紅)成立,是真問題——新檔不能靠 restore,改成換空殼。正3 整條折入,不駁回。
