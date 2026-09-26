severity: minor

## F1 `_esc_clean` 只濾 C0 控制碼,8-bit C1 逃逸序列(如 0x9B=CSI)沒濾
severity: minor
blocking: no
攻擊路徑(推論,終端行為依模擬器而定,故降級 minor):誰——任何能跑 `lumos loop escape`/`--withdraw` 的內部使用者(不需特殊權限,本來就自報不驗身分);入口——`--withdrawn-by`、`--reason`、`--desc`、`--stage` 這些自由文字欄位;送什麼——夾帶單一 0x9B 位元組(8-bit CSI)取代 `\x1b[` 兩位元組序列;拿到什麼——在支援 8-bit 控制碼的終端(部分舊終端/某些 locale 設定下的 xterm)執行 `lumos loop escape --list` 或撤回訊息時,該序列不會被 `_esc_clean` 濾掉(它只擋 `ch < " "` 與 `\x7f`,0x9B ≥ 0x20 逃過),仍可能被終端解讀成控制序列。`_esc_clean` 本體不在本輪差異裡,以下錨這輪新增、把使用者可控值餵給 `_esc_clean` 但仍可能留下 8-bit 序列的那一行:
引句:「            print(f"擋下:逃逸帳裡沒有 token {_esc_clean(target, 40)} 這一列,帳本沒動。看全帳(每列都印 token):\n"」

## F2 `lumos doctor` S14 段落印 `stage` 未經 `_esc_clean` 清洗(非本輪改動,但與本輪「清洗 token」的宣稱同一份逃逸列資料模型,提醒一併看)
severity: minor
blocking: no
攻擊路徑(推論):誰——能記手動逃逸的人;入口——`lumos loop escape <迴圈> --stage <站>`;送什麼——`--stage` 填入含 ESC(`\x1b[...`)的字串;拿到什麼——之後任何人跑 `lumos doctor` 觸發 S14「風險低計劃放行」段,`f"{k} {v}"`(`k` 即未清洗的 `stage`)直接印到終端,未走 `_esc_clean`,可能造成終端輸出被污染/游標搬移。doctor S14 那行不在本次 r2 diff 改動範圍內,錨不到;改錨 patch 裡同一類輸出(逐筆印帳本欄位)、且逐一把 `token`/`stage`/`desc` 送進 `_esc_clean` 的那一行,證明「本輪把同一批欄位清洗過但只清洗了 --list 這條輸出面,doctor S14 那條輸出面漏了同款欄位沒清洗」:
引句:「                print(f"    {str(r.get('ts') or '?')[:10]} {_esc_clean(r.get('token', '?'), 20)} [{sev_disp}@{_esc_clean(r.get('stage', '?'), 30)}] {_esc_clean(r.get('desc', ''))}"」

已看,無:
- `_plan_for_loop` 的路徑守衛(擋 `/`、`\`、`..`)在 POSIX 上足以把候選檔名鎖在 `Projects/` 內;NFC 只做正規化組合,不做相容分解,全形斜線／反斜線等混淆字元不會被檔案系統當成分隔符,不構成繞過。
- `--list`、撤回擋下訊息、撤回成功訊息裡的 `token`/`reason`/`by`/`desc`/`stage`/`rule`/`defect_ref` 均已改走 `_esc_clean`,涵蓋 round1 指出的「錯誤訊息沒清洗 token」。
- token 重複偵測用 `_escape_raw_rows` 全量比對後才動作,先擋才寫入,沒有 TOCTOU 視窗(寫入鎖 `_vault_write_lock` 包住讀-判-寫)。
- `--withdrawn-by` 明文寫「自報不驗身分」,round1 第三項屬設計已接受的風險並有執行期提示,非本輪新增缺口。
- `_escape_released_loops` 新增 `gate == "design-loop"` 與 `isinstance(nodes, list)` 檢查,修掉了「nodes 是字串時把第一個字元當迴圈編號」的資料混淆問題,方向正確;此路徑觸發前提是攻擊者已能寫 `.governance-log.jsonl`,屆時已具備更大破壞力,不在本輪重點。

共 2 條(F1、F2),皆 minor、皆不擋。
