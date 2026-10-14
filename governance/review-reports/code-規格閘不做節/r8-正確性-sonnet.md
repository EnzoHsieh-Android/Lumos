severity: major

以下是第八輪「正確性(修補鏡頭)」的結果。我讀了修補差異和 `scripts/lumos` 裡對應的函式,跑了三個小實驗(都在 scratchpad,已不需要保留):讀帳的錯誤位置換算、`cmd_loop_status` 遇到非物件行的行為、危險詞掃描對不可見字元的反應。

已讀,無 finding:
- 輕量審這條路(`_nogo_light_gate`):乾淨輕量審 → 放行這條走得通。曾有 major 或帶輪次的紀錄會正確改指 -std。
- `cmd_loop_status` 以 `readonly=True` 呼叫:沒有副作用。尾巴的 roster、severity、`_loop_gov_mark`、`_cap_hint_print` 全被 `if not readonly` 擋住。留痕重驗、跑滿回顧、落點、條款綁定都只讀。stdout 和 stderr 都收進 buffer,不印到終端。
- `_canary_ledger_rows` 的錯誤位置:對含壞位元組的帳,逐塊換算出的 `start`/`end` 與整本解碼得到的完全一致(實測 30–32 對 30–32)。真實帳 4356 筆讀完約 0.055 秒。
- 資料狀態五問,逐項:
  - 帳檔不存在:回空表,不出錯。
  - 帳檔是目錄:`OSError`,被 `_nogo_ctx` 接住並擋下講原因。
  - 非 UTF-8:索引這頭用替代字元照讀,審查輪那頭回 `exc`。
  - 壞行、超深巢狀行:跳過。
  - 沒有 -std 紀錄:回 `""`,只講怎麼開。
  - `spec_path` 缺或指到別的檔:正確擋下。
  - 此外,`cmd_loop_status` 自己的讀法比索引嚴格(見 finding 2)。

severity: major
blocking: 是 — 誠實流程「輕量審出 major → 開 -std → 過處置閘 → 實作 → 推送」在推送前走不通,得再開一輪完整審,而且擋下訊息看不出原因
引句:「hash 鏈對到這份計劃現在的內容、處置集合、留痕、引句、條款綁定、落點、跑滿回顧全照它」
問題:出口 (b) 比的是計劃「現在」的整份雜湊。實作完照鐵則一必須把 lands_in、驗證連結、`status: done` 寫回同一份計劃並同提交推送,所以每份誠實走 (b) 的計劃在推送時雜湊都對不上。出口 (a) 刻意只比被略過的那幾行,(b) 沒有對應處理。
擋下訊息也沒講原因:`last` 挑到的是 `⛔ DISPOSAL GATE FAIL (…: G3)` 橫幅,只有 G3 三個字。真正的原因「spec 於審計後被改動」印在更前面一行,被丟掉。
具體失敗情境:
1. 輕量審出 major,開 `X-std`,走完整迴圈過處置閘。
2. 實作並寫回計劃(改 `status`、補 `lands_in`),計劃位元組變了。
3. 推送時 `_nogo_std_gate` 回「X-std 的處置閘沒過(⛔ DISPOSAL GATE FAIL (X-std 輪 r1: G3))」。
4. 出口只剩在 -std 再記一輪完整審;零發現的空輪也得有席位、報告和留痕。
佐證:``file: `scripts/lumos:12112` ``(G3 訊息被丟掉)、``file: `scripts/lumos:9357` ``(`last` 的挑法)。
建議:(b) 比照 (a),認 -std 通過當下的凍結快照,只比被略過的行;或至少把 `[disposal] G3 hash` 那行帶進訊息。

severity: minor
blocking: 否 — 只在帳裡有非物件的行時才崩,而且推送前檢查崩潰等於擋下並印堆疊,沒有放行
引句:「UnicodeDecodeError 是 ValueError 的子類:帳不是 UTF-8、沒人裁紀錄時 cmd_loop_status 照原樣往上丟」
問題:`_nogo_std_gate` 只接 `(OSError, ValueError)`,但 `cmd_loop_status` 自己的讀帳迴圈在 `json.loads` 之後直接 `d.get("loop")`,沒有判斷是不是 dict。索引那頭的 `_canary_ledger_rows` 明確跳過非物件行,所以同一本帳在 (a) 沒事,到 (b) 才崩。
具體失敗情境:帳裡有一行 `[1,2]` 或 `5`,且某計劃的 `X-std` 有紀錄 → 實測 `cmd_loop_status(..., disposal=True, readonly=True)` 丟 `AttributeError`,沒被接住,整個 `_spec_gate_push_scan` 帶堆疊失敗。
同族還有:帳內任一行 JSON 壞掉,處置閘就回 rc2,(b) 整條不可用。這是處置閘原本 fail-closed 的設計,但和索引那頭的容忍度不一致,建議在說明裡寫明。
佐證:``file: `scripts/lumos:13459` ``(`d.get` 前沒有型別判斷)、``file: `scripts/lumos:9352` ``(except 範圍)。

severity: minor
blocking: 否 — 屬於威脅模型內的偶發貼上,繞過後危險詞判成風險低,但來源要有人刻意或剛好貼到特殊字元
引句:「再拿掉零寬字元(共用 _strip_zero_width;」
問題:版本 6 宣稱「夾零寬字元的危險詞也算」,但共用的 `_strip_zero_width` 只去 U+200B 到 U+200F 與 U+FEFF。U+2060(詞連接符)、U+00AD(軟連字號)、U+202A 到 U+202E(雙向控制字元)、U+034F、U+FE0F、Unicode tag 字元都沒去。
具體失敗情境:實測 `_door_keyword_hits` 對「退\u2060款」「退\u00ad款」「ｐａｙ\u2060ｍｅｎｔ」「退\u202a款」都回空,只有 U+200B 那一種被抓到。第七輪邊 2 同一族的洞只補了一半。
佐證:``file: `scripts/lumos:5000` ``(去除字元集)、``file: `scripts/lumos:8081` ``(`_door_scan_text`)。

severity: minor
blocking: 否 — 有出口(再審一輪 -std),只是重複審查的成本
引句:「有帶輪次的(多人審格式)→ 判不了」
問題:原編號已經走過完整設計審(帶輪次),就整條判不了。出口 (b) 只認 `<編號>-std`,不認原編號自己已經過了的處置閘。
具體失敗情境:實測本庫有風險低留痕的計劃 27 份,其中 4 份(約 15%)原編號帳上也有帶輪次的紀錄。這類計劃若不做清單略過了危險詞,即使原編號的完整設計審已過處置閘,仍被要求再開一個 -std 重審一遍。r6 版本不會這樣擋(讀帳時跳過帶輪次的紀錄),這是 r8 新增的行為。
佐證:``file: `scripts/lumos:9302` ``。
建議:帶輪次時,(b) 也試一次原編號的處置閘。

severity: minor
blocking: 否 — 文件和程式不一致,會誤導人走進死路,但擋下訊息本身指的是對的出口
引句:「推送前檢查只認不帶 `-std` 的原編號,所以照下面這行手寫記帳」
問題:這句是 `templates.md` 沒被改到的舊段落,但現在已經不成立:(b) 認 -std。底下還叫人把乾淨紀錄手寫記到原編號,並說「還是 major 就寫 plan_risk: high」。而原編號只要記過 major,light 就永久失效,手寫乾淨紀錄不可能放行。
具體失敗情境:`loop next` 回 escalate,依這段手寫一筆乾淨輕量審記到原編號 → 推送前仍擋;`plan_risk: high` 則是讓計劃退出推送前檢查,和新規則「出口只剩 -std」互相矛盾。
佐證:``file: `skills/lumos-design-loop/templates.md:71` ``。

最高等級 major,blocking 1 條。
