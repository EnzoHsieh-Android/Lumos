severity: major

## 三問

1. 分層與依賴方向:新函式 `_ns_tr_manual_clauses` 放在 `_ns_tr_sub_says_retire` 與 `_doctor_test_ref_lines` 之間,由 doctor 層呼叫、向下用 `clause_bindings`、`_strip_inline_markup`、`_ns_tr_retired`,方向跟既有一致(對照 `scripts/lumos:32389`、`scripts/lumos:32404`),沒有跨層直呼。
引句:「定義行照 _ns_test_ref_lines 同一支 clause_bindings 取。」

2. 命名與錯誤處理:`_ns_tr_` 前綴、docstring 風格、`try/except Exception: return []` 都照 `_ns_test_ref_lines` 的寫法(`scripts/lumos:31976`、`scripts/lumos:31996-31999`),一致;唯一小落差是守檔筆記新增的 WHY 缺必有鍵 [因:](見 F2)。
引句:「    except Exception:」

3. 第二種做法:有。取定義行本身沿用 `clause_bindings`(一致),但「這行有沒有掛 [manual:]」是自己用 `MANUAL_REF_RE.finditer` 對 `_strip_inline_markup` 後的行重新解析(`scripts/lumos:32383-32385`),不用 `clause_bindings` 已經算好回傳的 `manual` 欄與 `state`(`scripts/lumos:7210-7217`)。兩套判法已經分歧:(a) `clause_bindings` 要求 ≥4 字且有實字才算 manual(`_MANUAL_MIN_CHARS`,`scripts/lumos:5276`、`scripts/lumos:7210`),spec-trace 把 1~3 字的 [manual:] 當未標;新函式 `v and ...` 只要非空就算,會把 spec-trace 認為「沒標」的行列成候選。(b) `clause_bindings` 明訂「同行有 [test:] 與 [manual:] 以 [test:] 為準」(`scripts/lumos:7162`),新函式不管,同一行兩者都掛且下一層寫撤除時,`_doctor_test_ref_lines` 會先以 [test:] 列一筆、再以 [manual:] 列一筆,同一行重複兩筆(輸出面可見)。
引句:「        vals = [m.group(1).strip() for m in MANUAL_REF_RE.finditer(raw)]」

## F1 判 [manual:] 另寫一套,跟 clause_bindings / spec-trace 的判法分歧
severity: major
blocking: 是
引句:「        if any(v and not v.startswith("已撤除") for v in vals) and not _ns_tr_retired(slot_parse(raw)):」
說明:該重用 `clause_bindings` 回傳列的 `manual`/`state`(`scripts/lumos:7210-7217`),或抽出共用判斷;至少套用 `_MANUAL_MIN_CHARS` 與 [test:] 優先,否則 spec-trace 與 doctor S20 對「這條有沒有 [manual:]」答案不同、且同行雙掛會重複列。

## F2 守檔筆記新增 WHY 缺必有鍵 [因:]
severity: minor
blocking: 否
引句:「S20 散文撤除候選也看掛 `[manual:]` 的條款(整篇沒有 `[test:]` 也看;」
說明:同檔同類 WHY(例如 S20 那條 `scripts/lumos` 對應筆記行)都帶 [出處:][因:],這條只有 [出處:][不選:][test:],缺 [因:](CLAUDE.md 表格的 WHY 必有鍵)。

## 另判:計劃筆記與守檔筆記
- 守檔筆記 `lumos-cli-read.md`:WHY 放在 S20 那條後面、日期前綴方括號寫法同該檔第 26 行既有樣式、`updated` 同步、test 綁定名與新測試一致,除 F2 外一致。skill 文件 `04-自檢與健康.md` 的句子同步改了,一致。
- 計劃筆記 `Projects/撤除候選也看manual條款_計劃` 不在這份 patch 內(patch 只含守檔筆記、程式、測試、skill 文件),無法判寫法是否與同類計劃一致 ⚠ 交編排者。

不對齊共 2 條,其中 major 1 條
