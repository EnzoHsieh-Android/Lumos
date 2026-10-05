severity: minor

# 架構對齊審查 第 2 輪

## 問 1 分層與依賴方向
讀另一道檢查的設定:`_nodehome_tag_exempt` 用 `_note_shape_config` 加 `_ns_test_refs_mode` 兩步讀,跟既有寫法一致,沒有跨層直呼。
引句:「gate, _w = _note_shape_config(cfg_text)」
既有碼佐證: `scripts/lumos:29125`(同樣先取 gate 再丟給 `_ns_test_refs_mode`,29127 取 `[0]`)。差別只在第三參數 staged,這裡寫死 False;因為 test_refs 在推送前才擋,語意合理,不列。

不對齊 1:豁免旗標事後塞進 cfg,同一個旗標又走兩條傳遞路徑。
引句:「cfg["tag_exempt"] = _nodehome_tag_exempt(cfg_text)」
cfg 事後塞鍵在 `scripts/lumos` 沒有先例:鄰居都在 `_nodehome_config` 內一次算好(`scripts/lumos:26554` 起,`cfg["mode"]`、`cfg["max_files"]` 在 26600、26606)。而且 `_nodehome_mark_note_content` 用 kwarg 收、`_nodehome_evaluate` 用 `cfg.get("tag_exempt")` 收,同一個值兩種傳法;另一個 `_nodehome_config` 呼叫端(`scripts/lumos:27680`)不會有這個鍵,靠 `.get` 的預設值才不炸。
severity: minor
blocking: 否 + 結構對(單向由上層算好往下傳),只是旗標來源與傳遞方式不統一,沒有造成第二種判定邏輯。

## 問 2 命名與錯誤處理
命名:`tag_exempt`、`sig_t`、`_nodehome_tag_exempt` 同前綴 `_nodehome_`,與同檔 `sig`、`_nodehome_strip_test_tags` 一脈;清單符號改用既有 `_NOTELINES_BARE_LIST_RE`,上輪的第二套正則已收掉。
引句:「if k and (not line.strip() or _NOTELINES_BARE_LIST_RE.match(line)):」
既有碼佐證: `scripts/lumos:28493`(`_NOTELINES_BARE_LIST_RE` 定義)。
`_nodehome_tag_exempt` 讀不到設定時由 `_note_shape_config` 與 `_ns_test_refs_mode` 自己處理,函式內不另做 try,與 `scripts/lumos:3968`、`29125` 的呼叫端一致。另把 `_l` 改成 `_ln` 避開 ruff,屬同檔慣例。無不對齊。

## 問 3 第二種做法
節點快照同時存 sig 與 sig_t:`sig` 與 `sig_t` 並存在 `_nodehome_parse_note` 沒有直接先例,但它是同一個解析結果的兩個視角、由同一函式一次算,不是另一套演算法;比對處用 `sk = "sig_t" if … else "sig"` 選鍵,兩處(`_nodehome_mark_note_content` 與 `_nodehome_evaluate`)寫法相同,沒有分岔。
引句:「sk = "sig_t" if tag_exempt else "sig"」
測試內函式內匯入:檔頭 `scripts/test_lumos.py` 沒有頂層 import json,既有測試大量在函式內寫 `import json as _j`/`_json`,本 diff 照做。
引句:「    import json as _j」
既有碼佐證: `scripts/test_lumos.py:3582`、`3658`、`3933`(同寫法)。
唯一值得記的第二種傾向:`sk` 選鍵兩處各寫一次,若再有第三處比對 sig 就會漏;目前只兩處,不升級。

## 結論
只有一條 minor(cfg 事後塞鍵加雙路傳遞)。上輪的正則重複已確實改用既有常數,這輪修正沒有引入新的第二種做法。

總結:不對齊共 1 條,其中 major 0 條
