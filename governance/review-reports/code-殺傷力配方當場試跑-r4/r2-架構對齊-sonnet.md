severity: major

# 架構對齊-sonnet(另開迴圈第 2 輪)

## 三問

1. 分層與依賴方向:`_kill_old_bad`/`_kill_new_bad` 放在 `_kill_judge_file` 正下方,判法與 `cmd_guard_kill` 原地擋共用同一支,方向是 guard kill 往下呼叫判法層的小謂詞,沒有倒灌或跨層直呼,對齊。`_guard_kill_pick` 兜底印行沿用 `_kill_add_warn` 的「判斷自己出錯不擋、印一行、照做」。對照:file: `scripts/lumos:14172`、file: `scripts/lumos:14216`。唯一的結構問題在第 3 問。
2. 命名與錯誤處理:回傳「說明或空字串」的慣例與 `_kill_path_issue`(是回空字串、不是回原因)一致;結果記成 verdict=error 的寫法與 `cmd_guard_kill` 既有的 `results.append({**r, "platform": plat, "verdict": "error", ...})` 一致;兜底印行用 `⚠ 提醒:` 前綴與 `_kill_esc(ex)`,與 `_kill_add_warn` 一致。小出入見 F2。
3. 第二種做法:`--json` 的替身字元跳脫在行內另寫了一份 Cs 跳脫,專案已有 `_kill_esc`(file: `scripts/lumos:14025`),而且同一支檔的 `_kill_rm_show` 已經用「`_kill_esc(json.dumps(..., ensure_ascii=False))`」印 JSON 文字(file: `scripts/lumos:14779`),正是同功能的既有做法。見 F1。

## F1 --json 另寫一份行內替身字元跳脫,既有 _kill_esc 套在 json.dumps 輸出上已是現成做法
severity: major
blocking: 是
引句:「print("".join(f"\\u{ord(c):04x}" if unicodedata.category(c) == "Cs" else c for c in json.dumps(」
file: `scripts/lumos:14025`(`_kill_esc` 本體,類別走共用 `_PATH_SPECIAL_CATS` 即 Cc/Cf/Zl/Zp/Cs)、file: `scripts/lumos:14779`(同檔 `_kill_rm_show` 對 json.dumps 文字套 `_kill_esc` 的先例)、file: `scripts/lumos:29437`(跳脫類別只有一份的家規註解)
1. 同功能第二種做法:新行內邏輯是 `_kill_esc` 只取 Cs 的子集,等於另抄一組判準;`_PATH_SPECIAL_CATS` 上方註解明說「類別只有這一份、日後補類別要改兩處」正是要避免的事。
2. 行為上也分岔,最小重現(以 `_kill_esc` 的類別與新行內寫法對同一份 JSON 文字各跑一次):輸入 {"r": "a\ud800b‮中"},新寫法輸出 `{"r": "a\\ud800b‮中"}`(U+202E 雙向覆寫原樣印到終端,repr 顯示為真字元),`_kill_esc(json.dumps(...))` 輸出 `{"r": "a\\ud800b\\u202e中"}`;兩者 json.loads 回來都等於原物件、都是合法 JSON。也就是這條路徑上同類字元(Cf 方向覆寫)有的鄰居跳脫、這裡不跳脫,而 `_kill_rm_show` 的註解與代碼審第 1 輪資安席的理由(筆記來自不可信提交,別讓控制字元蓋掉工具輸出)同樣適用於這份 JSON。
3. 建議:改成 `print(_kill_esc(json.dumps({...}, ensure_ascii=False)))`,刪掉行內版本。一般中文不受影響(類別是 Lo,不在集合內)。

## F2 兩支新謂詞命名方向與鄰居不一致、放置位置離家
severity: minor
blocking: 否
引句:「def _kill_old_bad(r):」
file: `scripts/lumos:14109`(`_kill_path_issue`:`*_issue` 回原因)、file: `scripts/lumos:14196`
1. `_kill_old_bad`/`_kill_new_bad` 讀起來像布林(「是不是壞的」),實際回「說明字串或空字串」,與鄰居 `_kill_path_issue`(同樣的回傳形狀、名稱叫 issue)不一致;呼叫端 `_bad = _kill_old_bad(r)` 靠區域變數名補意思。結構對,只是命名慣例不一。
2. `_kill_detail_str`、`_kill_inv_has` 放在 `cmd_guard_kill` 之後、`_guard_kill_cfg` 之前,而其餘判法小謂詞都聚在 `_kill_judge_file` 一帶(約 14172 至 14216);`covers` 的清單檢查則直接行內(`_cov = res.get("covers")`)而沒有比照 `_kill_detail_str` 做成小函式。三處「欄位被手改成怪型別時不當掉」的處理各用各的形狀(輔助函式、行內三元、try/except TypeError)。

不對齊共 2 條,其中 major 1 條
最高等級:major,blocking 共 1 條
