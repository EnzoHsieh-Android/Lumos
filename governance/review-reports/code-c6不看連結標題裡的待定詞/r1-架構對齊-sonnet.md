severity: minor

## 問一:分層與依賴方向
既有做法:遮蔽在「遮好的行」那一層做完(`_drift_pending_clauses` 先呼叫 `_drift_mask_quotes(_drift_mask_settled(line))`),`_drift_pending_clause` 只吃遮好的子句判有無待定詞,見 `scripts/lumos:33196`、`scripts/lumos:33159`。本 diff 把遮連結放進判定函式內,沒有跨層直呼(只呼叫已有的 `WIKILINK_RE`,同檔),但遮蔽散在兩處。不能直接放進遮好的行是對的:`_drift_pending_links` 還要在遮好的子句上 `WIKILINK_RE.finditer` 找連結(`scripts/lumos:33211`),所以放判定裡有理由,屬結構上可接受的偏離。⚠ 判不準這算「第二種做法」還是合理分工,故只給 minor。

## 問二:命名與錯誤處理
沒有新名字,局部變數 `bare` 與同檔其他遮蔽變數(`masked`)用詞略不同;函式 docstring 首句仍寫「這個子句(遮好的)」,但現在內部又再遮一次,措辭略不一致。無錯誤處理差異(同檔遮蔽函式都不丟例外)。

## 問三:第二種做法
遮法沿用既有的「等長佔位字」`re.sub(lambda m: 佔位字 * len(...))`,與 `scripts/lumos:33185` 一致;佔位字沿用 `_DRIFT_QUOTED` 常數,沒有新常數。語意上「QUOTED」被拿來代表「連結」,名稱不貼切,但因為遮的字元只用在判詞比對、不會被當作遮好的行輸出,沒有行為衝突。測試寫法沿用 `_df_repo`/`_nh_file`/`_df_commit`/`_df_find`/`_c6_ln`/`check`(對照 `t_drift_c6_detects_pending_clause_to_settled_note`),一致。

## F1 遮連結放在判定函式而非遮蔽管線
引句:「    bare = WIKILINK_RE.sub(lambda m: _DRIFT_QUOTED * len(m.group(0)), cl)」
severity: minor
blocking: 否

對照 `scripts/lumos:33192`(新)、`scripts/lumos:33195`(`_drift_pending_clauses` 的遮蔽管線)、`scripts/lumos:33185`。其餘兩種遮蔽在管線入口一次做;本案在判定處再遮一次。有技術理由(連結要留給 `_drift_pending_links`),結構上算可接受,建議在 docstring 或計劃註明「連結不能進管線遮」的原因。

## F2 常數 `_DRIFT_QUOTED` 拿來遮連結,名稱不貼切
引句:「    return any(w in bare for w in _DRIFT_PENDING_WORDS) and _DRIFT_MASK not in cl」
severity: minor
blocking: 否

對照 `scripts/lumos:33179`。沿用既有常數沒有第二套佔位字,方向對;僅名稱語意(quoted)與用途(連結)不符。

不對齊共 2 條,其中 major 0 條
