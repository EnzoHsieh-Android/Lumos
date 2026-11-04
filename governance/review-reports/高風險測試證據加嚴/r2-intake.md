# r2 收貨紀錄

## 席位收貨

四席報告從逐字稿存。正確性席、邊界席首交的「引句:」沒有用「」包原文,退回只補引號(內容不變),補交版才記帳。編號:正確性 1–15 記 c1–c15、邊界 1–15 記 b1–b15、整合 1–20 記 i1–i20、架構對齊依報告出現順序 1–12 記 a1–a12(a1 判定檔讀法、a2 先紅模式沒有單一判斷函式、a3 首筆帳重複讀、a4 治理帳不同趟與取最晚、a5 欄位白名單、a6 生效常數取值、a7 簽核人與答 n 回傳碼、a8 gov 去重 token、a9 表格拆格、a10 找節、a11 落點漏 bound-tests-gate、a12 推送前逐份檢查寫死風險低)。

機械收貨:
- quote-check:四份補交後全數錨定。
- refcheck:四份引的 file:line 全部存在。
- seat-check:只觀測,正確性 2、邊界 3、架構對齊 1 則「沒提到某份材料檔名」,引句都錨在快照上,不影響。

世界查證(修前,Enzo 要求「搜世界解」):fail-to-pass 基準重播——devops-cli `ci fail-to-pass`(https://github.com/dan-petty/devops-cli/pull/1596;重播環境全紅、檢查形同虛設的坑 https://github.com/dan-petty/devops-cli/issues/3124)、PRProof(https://github.com/pedronav1310/prproof)、verify-fix(https://github.com/AndrewDongminYoo/andrew-code-agent/pull/127);GFM 表格規則(格內 `\|`)。用提交順序認定先寫測試沒有找到可靠工具。

## 依根因分組與去向

使用者裁(2026-11-04 AskUserQuestion):先回「搜世界解」,看完世界解後裁「換成基準重播(推薦)」。

| 組 | 根因 | 發現 | 去向 |
|---|---|---|---|
| G1 | 沿用風險低推送前檢查,接縫裡寫死風險低(欄位白名單、done 寬待、全靠人驗走小改動閘、已做完短路、輕量審、自動記逃逸、寫死字串) | c1 c2 c3 c4 c8 c9 c10 c15 b1 b14 i5 i8 i10 a5 a12 | 折:整類拿掉——不再沿用 `_spec_gate_push_one`、不再有 `red_first` 留痕,改成推送前基準重播(d1);不自動記逃逸 |
| G2 | 開關與生效基準(判定檔讀法與過期、迴圈編號對不上、首筆帳讀不到、生效常數取值) | c5 c6 b3 b15 i6 i9 i18 a1 a2 a3 a6 | 折:不判設計審過了沒;開關改看計劃 `created` 對純日期常數(d6),值事先訂好 |
| G3 | 靜態檢查少了測試名互異與存在 | c7 b2 i4 | 折:重播前直接呼叫 `_spec_gate_twoway_static` 與 `_clause_check_twoway`;本計劃條款改成一條一支測試 |
| G4 | 只因連到被拉進來的計劃會擋別人 | c11 b8 | 折:只看推送範圍改到的計劃檔,重播、查表、查簽都一樣 |
| G5 | 預期值表的節、表範圍、拆格跳脫、空格子、條款欄寫法、指紋碰撞 | c12 b4 b5 b6 b7 a9 a10 | 折:`_h2_section_lines` 加選填參數回報出現次數;表範圍到第一個非 `|` 行為止、之後再出現表格列算錯;`\|` `\\` 還原;四格不得空;條款欄嚴格 `S` 加不以 0 開頭的數字;指紋改用 JSON 編碼 |
| G6 | 簽核指令出口、事件欄位、統計去重、讀帳趟數、提示與逾時 | c13 c14 b9 b10 b11 b12 b13 i12 i13 i19 i20 a4 a7 a8 | 折:讀一次文字;答 n rc1;帶 --by/--ref rc2;不是需要簽的計劃 rc2;欄位 origin/who(照 `_e2e_who`)/token/note 截 200;表放進提示字串;`_gov_row` 帶 token 與 origin;效能說法改成另讀一趟 |
| G7 | 跟著改的說法、手冊流程接點、版號、第二批漏列、撤除條件、落點 | i1 i2 i3 i7 i11 i14 i15 i16 i17 a11 | 折:做法第 8 點逐處列出(含 docs 兩份、INDEX、05、design-loop reference、code-loop SKILL、雙向門計劃);pre-push 改中性措辭;升小版號寫 CHANGELOG;第二批補 Mockito 與 r1 漏列的坑;RETIRE-IF 改數擋下事件與逃逸描述;lands_in 補 Systems/bound-tests-gate;i3 的順序衝突因不再有規格閘先紅而消失 |

全部 62 條折入,0 條放行,0 條重現不到。
