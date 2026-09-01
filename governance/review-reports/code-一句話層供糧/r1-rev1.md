# 審查結果(單席通才,sonnet)

**B-1**|minor|否(有 fallback、不 crash,但違反本函式自己宣稱的優先序)
引句:「if s.startswith("> 白話:"):」(補引 2026-09-01 續談;原引句含省略)
file: scripts/lumos:6016
實測:88 篇現存「> 白話」行裡有 2 篇用全形冒號「> 白話:」(Projects/panel收斂判準改革_計劃.md:32、Projects/標籤結構收編_計劃.md:27),半形比對抓不到,靜默跌回②/③,吃掉①優先於②的設計意圖。

**B-2**|minor|否(latent,現在無資料命中)
引句:「_GIST_SENT_RE = re.compile(r"^.{0,79}?[\u3002!?;\uff1b]")」(補引 2026-09-01 續談;原引句轉寫了跳脫碼)
file: scripts/lumos:5981
漏全形 !(FF01)?(FF1F)——首句 >80 字以全形驚嘆/問號收尾會誤判無句界硬截。grep 全庫 0 筆現踩,充值庫成長後遲早撞。

**B-3**|minor|否
引句:「for raw in body.split("\n")[:20]:」
file: scripts/lumos:6013-6016
未過 fenced code 過濾;前 20 行內程式碼圍欄裡的字面「> 白話: …」示例會被誤當真標記。邊界案例,未見真實撞例。

**B-4**|minor(記錄用,非新增缺陷)|否
引句:「text = (env.vault / rel).read_text(encoding="utf-8-sig")」
file: scripts/lumos:6009
top-5 各補讀一次全文屬重工;但單篇 read_text 模式既有十幾處先例,每次 loop next 最多 5 次,量級遠小於 git log 教訓規模;無 INVARIANT 被破。

**B-5**|minor|否
引句:「if s[:2] in ("- ", "* "):」
file: scripts/lumos:6025
只認 dash+空白;"-\t內容" 不剝,dash+tab 原樣留在輸出。純格式瑕疵。

## 必答 8 篇逐條判定
- slim-get/slim-install/slim-uninstall/canary-audit(4 篇):diff 零交集——不影響。
- 測試假綠形態:有交集(t_gist_layer)。斷言比對具體非平凡字串,有鑑別力;唯「誠實缺席」條 g7=="" 分不出③分支與例外吞——兩路徑設計上都回空,不構成違反,留一句提醒。
- design-loop:只加建議行欄位,phase 機械脊椎未碰——不影響。
- lumos-cli-read:讀寫分軌沒破,_gist 純讀不寫;效能觀察見 B-4,無 INVARIANT 破。
- lumos-cli-lifecycle:未涉 install/bootstrap/deinit——不影響。

severity: minor
