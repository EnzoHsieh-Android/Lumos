否決成立
- scripts/test_lumos.py:23788：只驗 advisory 正常運作時 `loop next` 維持 rc1，未注入 `_el_related_nodes` 例外，也未比對例外前後既有 JSON／文字輸出；未覆蓋 spec 的 fail-open 核心合約。
- scripts/test_lumos.py:23822：`new` 僅驗正常命中時 rc0、檔案建立，未注入候選收集或輸出階段例外，無法證明例外時 rc、既有輸出及建檔結果不變。
- docs/lumos-toolchain-knowledge/Projects/圖譜進迴圈入口栓_計劃.md:52：上述缺口正落在 spec 明定的共同鐵則，屬應補齊後才能放行的重大驗收缺失；靜態實作雖有 try/except，測試未鎖住此合約。
- scripts/lumos:5811：OR 收集未抽成與 `cmd_search` 共用 helper，確實偏離 spec:17；但它重用 `_search_visible_lines`、`_rank_score_candidates`，且偏離已由 d1 記帳並設重驗條件，我接受為非阻擋性技術債。
- scripts/lumos:5987：未見足以直接造成錯誤 rc、破壞既有輸出或資料損壞的實作缺陷；A/B 掛點皆有例外隔離，B 也在建檔前取候選、建檔後告知。
- scripts/test_lumos.py:23770：唯讀環境實跑因系統無可用 temporary directory 而未進入案例，故不能把本次執行失敗算成 patch 功能紅燈；否決依據是測試內容的合約覆蓋缺口。

severity: major
