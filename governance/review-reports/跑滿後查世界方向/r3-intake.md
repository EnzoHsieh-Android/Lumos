# r3 收貨紀錄

## 席位收貨

四席報告從逐字稿存,四份原本就是正規化格式。引句檢查:邊界、整合、架構對齊全數錨定;正確性 8 句有 1 句錨不到(第 4 條裡只引了「已有人裁」四個字,低於 10 字下限),那條另有一句全長引句錨得到,照收。審查席臨時目錄 `/tmp/lumos-seat-work/跑滿後查世界方向/` 收齊後確認是空的、沒有程序開著,已刪。編號:正確性 1–8 記 c1–c8、邊界 1–7 記 b1–b7、整合 1–10 記 i1–i10、架構對齊依出現順序 1–6 記 a1–a6(a1 三種情況沒指名單一處、a2 verdict 先去空白跟鄰居不同、a3 網址沒對齊 `_secev_target_host`、a4 提示散在三處、a5 帳上新欄位沒讀者、a6 借用清單跟做法對不上)。

## 先查世界

### G1 網址檢查(同類連兩輪:r2 空白、r3 埠號丟例外)

查了「URL normalization duplicate detection pitfalls default port trailing slash RFC 3986 equivalence」「LLM agent research citations validation check URLs exist format check does not verify research」:
- RFC 3986 第 6 節只把 scheme 與主機大小寫、預設埠、點段列為安全的同義改寫;結尾斜線、首頁檔名不保證同一頁,建議連過去看轉址(https://en.wikipedia.org/wiki/URI_normalization;NormalizeUrl.Net 因此預設不去結尾斜線,https://www.nuget.org/packages/NormalizeUrl.Net)。
- 引用網址 3–13% 是編的、5–18% 連不上,要連網查存活與讀內容才驗得到(arXiv 2604.03173,https://arxiv.org/abs/2604.03173)。
方向:要換 — 離線的網址正規化永遠補不完同頁寫法,而格式檢查本來就證明不了查過;整類拿掉正規化,只驗開頭與空白、整串比重複,同頁不同寫法列天花板一。

### G2 三種情況的判定(r2 G1 只修了檢查那一側)

修法:同一份回顧的判定由一支函式提供、各呼叫端共用,是本 repo 既有的做法([[Systems/loop-retro]] WHY d7「五處共用同一支判定」);不另查世界。

## 依根因分組與去向

| 組 | 根因 | 發現 | 去向 |
|---|---|---|---|
| G1 | 網址解析與正規化(`.port` 在 try 外丟例外、主機名比既有寬、路徑斜線、天花板列不全) | c1 c8 b1 b3 b4 b5 i3 a3 | 折:整類拿掉——不解析網址,`url` 去頭尾空白後以 `http://` 或 `https://` 開頭、後面至少一個字、整串沒有空白字元;整串相同算重複;天花板一補列大小寫、預設埠、結尾斜線、參數順序;PRIOR-ART 補 RFC 3986 與引用網址研究 |
| G2 | 三種情況沒有單一判定處,「不管」的舊迴圈漏進統計與記帳、帳上新欄位沒讀者、「沒填」口徑沒定義 | c2 c3 b2 a1 a5 i7 | 折:新函式 `_cap_world_case` 判三種情況,`_cap_retro_check` 回傳帶出,`--record` 與 `retro-stats` 只讀它;拿掉 `world_verdict` 帳欄(結論只在回顧檔);統計只數「要求」而且已記回顧的迴圈,三個數,不再有「沒填」;S6 補不管的舊迴圈填了非物件也不進統計、不丟例外 |
| G3 | CHANGELOG 只記對外發版,寫一條就撞版本單源守衛 | i1 | 折:寫明這次不發版、不寫 CHANGELOG(理由與 `RELEASING.md` 人裁);相容二改字 |
| G4 | 提示的條件與位置(新句無條件會在可以停時印、accept-risk 也被叫去查、`canary record` 擋下與處置閘第八步沒提、同句散三處) | c4 c7 i4 a4 | 折:新句收成 `_CAP_WORLD_HINT`、`_CAP_WORLD_FILL` 兩個常數;查方向那句只接在既有「要破例再開一輪…」條件子句前;補 world_check 那句只在最新人裁是 extra-round 而且是要求時印,加進 `_cap_retro_fix_cmd`(擋下訊息與處置閘第八步共用);S7 補不印的案例 |
| G5 | version 與空骨架、ts 邊界的口徑(S5「不論 version」跟做法矛盾、bool 排除沒測、空骨架與真值判斷、ts 等於常數與跨時區) | c6 i5 i6 b6 b7 | 折:version 型別照 `type(v) is int`;S5 改成 version 1 或 2,補 "2"、2.0、true 判不過與 ts 等於常數、跨時區同一刻算要求;沒填的判定改成逐鍵比骨架、不用真值,S4 補空清單、空字串、false、0、多鍵判不過 |
| G6 | 生效常數與合併日的耦合、生效日前既有測試全落在「不管」 | c5 i8 | 折:第 7 點加兩支測試——常數解得開;最後一次改到常數那行的提交日期不晚於常數(拖到常數之後才合併會紅);產生器那份 world_check 另用 ts 不早於常數的人裁走一次要求路徑;相容三改寫 |
| G7 | 同步點與措辭(漏 `docs/心智模型.md`、「方向:」當檢索詞太常見、起因指的計劃在本 repo 查不到、verdict 去空白跟鄰居不同、借用清單對不上) | i2 i9 i10 a2 a6 | 折:同步點補心智模型流程圖;回頭條件與寫回改用整串固定前綴 `方向:對|要換|判不準 —`;起因補計劃連結與卷證路徑並註明分支未合併前查不到;verdict 原值直接比(同 `_RETRO_FAMILIES`);借用清單拿掉 `_cap_real_cutoff`、改寫 `_cap_retro_fix_cmd` 的用途 |

整合席另提回退段沒提 retro-stats 的統計段(沒編號):折,回退段補上。

## 重現

| 發現 | 怎麼試 | 結果 |
|---|---|---|
| b1、c1 | `python3.14 -c "from urllib.parse import urlsplit; u=urlsplit('http://a.com:abc/x'); print(u.hostname); u.port"` | HIT:hostname 是 `a.com`,讀 `.port` 丟 ValueError(三席各自實測一致,編排者重跑同樣) |
| i1 | 讀 `CHANGELOG.md` 開頭與 `t_version_single_source` | HIT:只記發版、不留未發布區塊,測試釘版本常數與第一筆一致 |
| c2、b2 | 讀 `cmd_loop_retro_stats`:`key == "recorded"` 就取 data,不分情況 | HIT |
| 折入後 | `python3.14 scripts/lumos spec-gate Projects/跑滿後查世界方向_計劃 --no-run` | 重現:rc0,8 條全標、懸空 8(測試還沒寫) |

本輪沒有重現不到、沒折也沒放行的發現。
