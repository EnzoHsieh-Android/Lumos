severity: major

這份 diff 有 3 個獨立的當機點,另有 3 條較輕的問題。診斷用的 fuzz 腳本和測資放在 `/private/tmp/lumos-seat-work/code-資安護欄唯讀盤點/邊界-sonnet/`(`fuzz.py`、`v1` 到 `v5`)。我拿 fuzz 腳本把控制項與 inventory 的每個欄位依序換成 23 種怪值,共 1173 個案例,得到 29 次當機,都落在下面三組根因。

## 邊界一覽

這些輸入都處理得對:
- 2000 層深目錄:回 `enumeration_failed`、rc2,沒有當機。
- 中文與空白路徑,以及 `null`、數字、單層陣列這類欄位值:乾淨地擋成 `invalid_record` 或 `invalid_block`。
- 不存在的 `--vault`、指到檔案的 `--vault`、同層多個圖譜:都擋下並回 rc2。
- 剛好 10000 檔、剛好 2MiB:邊界判斷正確。

## Finding 1

severity: major
blocking: 是

- **位置:**`_sc_source`。
- **問題:**`source.kind` 不是字串時,`{...}.get(kind)` 直接拋 `TypeError`,整個指令印 traceback 就結束。報告和錯誤清單都沒產出,也不會退出 2。
- **例:**
  - 輸入:`{"schema_version":1,"controls":[{"id":"c1","source":{"kind":[]}}]}`
  - 預期:列 `invalid_record`、rc2、JSON 仍可解析。
  - 實際:
    ```
    File ".../scripts/lumos", line 6797, in _sc_source
    TypeError: cannot use 'list' as a dict key (unhashable type: 'list')
    ```
  - `kind` 為 `{}` 或 `[[]]` 也一樣。
- **重現:**
  ```
  python3.14 scripts/lumos --vault <v1> security list --json
  ```
  `<v1>` 的 `Systems/a.md` 內放上面那一塊專用登記。
- **影響:**一份壞登記就讓整個盤點交不出報告。這違反計劃的「錯誤進 `errors`、rc2、JSON 仍可解析」。
- **缺的測試:**diff 的測試只有一般壞值(例如 `kind` 寫錯字串),沒有型別錯誤的 `kind`。
- 引句:「"requirement": ("kind", "claim", "decision_ref")}.get(kind)」

## Finding 2

severity: major
blocking: 是

- **位置:**`_secinv_inv_items` 和 `_secinv_inventory_problems` 一帶。
- **問題:**inventory 的 `assets[i].id` 不是字串時,`_secinv_inv_items` 只記一條問題,卻照樣 `ids.append(it.get("id"))`。後面 `set(...)` 遇到不可雜湊的值就拋 `TypeError`。
- **例:**
  - 輸入:`"inventory":{...,"assets":[{"id":[],"description":"x"}],"surfaces":[]}`
  - 實際:
    ```
    aset = set(_secinv_inv_items(cand["assets"], ...))
    TypeError: cannot use 'list' as a set element (unhashable type: 'list')
    ```
- **同根的第二條路徑:**
  - `surfaces[i].asset_ids` 含 `[1]` 這種元素時,`_secinv_str_list` 已記問題。
  - 但下一行 `any(x not in aset ...)` 沒有等 `ip` 為空才跑,元素不可雜湊就當機。
  - 輸入:`"surfaces":[{"id":"s1","asset_ids":[[1]],"description":"d"}]`,其他欄位正常。
- **同族:**這兩處是同一種模式,在 fuzz 中各有多筆當機。
  - 先記問題,不停下來,後面照用壞值。
  - 修法應整類處理:壞型別的值一律不進集合或字典查詢。
- **缺的測試:**測試只有 `assets` 重複 id 之類的一般壞值,沒有 id 或 `asset_ids` 元素為容器型別的案例。
- 引句:「aset = set(_secinv_inv_items(cand["assets"], ("id", "description"), "assets", ip))」

## Finding 3

severity: major
blocking: 是

- **位置:**`cmd_security_list` 的 JSON 路徑。
- **問題:**登記裡任何字串欄位含孤立代理字元(JSON 的 `"\ud800"`)時,`json.dumps(..., ensure_ascii=False)` 產出的字串無法編成 UTF-8,`sys.stdout.write` 拋 `UnicodeEncodeError`。
- **例:**
  - 輸入:`source.claim` 或 `revision`、`scope` 等任一字串欄位寫成 `"\ud800x"`。
  - 預期:`--json` 輸出單一合法 JSON,最差也是 `invalid_record`。
  - 實際:`sys.stdout.write(_json.dumps(rep, ensure_ascii=False, indent=1) + "\n")` 拋 `UnicodeEncodeError: ... '\ud800' ... surrogates not allowed`,stdout 是空的。
- **範圍:**fuzz 裡 `revision`、`source.*`、`assets[0]`、`scope`、`trust_boundary`、`owner`、`exception.reason`、`replacement_id` 等約 20 個欄位都中。
- **對照:**文字模式不會當機,因為 `_kill_esc` 會跳脫代理字元(類別 Cs)。
- **影響:**「JSON 模式恆為單一物件」的合約在這條輸入上破功。
- **缺的測試:**測試有 JSON 純度檢查,但沒有代理字元輸入。
- 引句:「sys.stdout.write(_json.dumps(rep, ensure_ascii=False, indent=1) + "\n")」

## Finding 4

severity: minor
blocking: 否

- **位置:**`_secinv_select_vault` 對 `--vault` 的處理。
- **問題:**`--vault` 只檢查「是目錄」,不檢查像不像圖譜。
- **例:**
  - 輸入:`--vault <空目錄>`
  - 實際:`read_complete: true`、`registration_complete: false`、rc0,文字模式只印「沒有任何登記條目」。
  - 預期:這是「指定的路徑不是圖譜」的輸入錯誤。
- **影響:**自動化只看 rc 時,把 `--vault` 打錯成別的目錄會得到 rc0 的「完整讀取」。
- **補充:**實際會遍歷整個目錄樹,例如指到家目錄。
- 引句:「return (p, None) if p.is_dir() else (None, f"--vault 指的不是目錄: {vault_arg}")」

## Finding 5

severity: minor
blocking: 否

- **位置:**`_secinv_entry_kind`。
- **問題:**它先判是不是捷徑,再看副檔名。圖譜裡任何捷徑,包括指向 `.png` 的 `hosts.png`,都列 `symlink_rejected`,`read_complete` 變 false,整體 rc2。
- **例:**`v2/hosts.png -> /etc/hosts` 或 `.trash/lnk -> ../Systems`,實測 rc2。
- **影響:**與其餘步驟的只讀策略一致,但對不相干的檔也升級成讀取不完整。若這是計劃 d1 認定的保守取捨,請 orchestrator 對照計劃 d1 確認;我不確定,標 ⚠。
- 引句:「errors.append(_secinv_err("symlink_rejected", nfc(rel), detail="捷徑不跟隨、不讀"))」

## Finding 6

severity: minor
blocking: 否

- **位置:**`--json` 輸出。
- **問題:**文字模式會把雙向控制符跳脫成 `\u202e`,JSON 模式卻原樣輸出 U+202E,因為 `ensure_ascii=False` 只跳脫 C0 控制字元。
- **例:**`claim` 為 `"ab\u202ecd"` 時,`--json` 的 stdout 是原始 U+202E 位元組。
- **影響:**JSON 本身合法。但人用終端機看管線輸出時會被反轉顯示,與文字模式的防護不一致。
- 引句:「sys.stdout.write(_json.dumps(rep, ensure_ascii=False, indent=1) + "\n")」

## 驗收條款能否寫成會紅的測試

Finding 1 到 3 都能。每一條都是一行輸入加 `main()` 或 `cmd_security_list`,斷言 rc==2 且 JSON 可解析,現在會紅。diff 附的測試是 `r1-tests.patch`,我看了測試檔裡 S9、S10 的相關段落(NFC 撞名、2MiB、64MiB、10000 檔),它們涵蓋了容量邊界,但沒有型別錯誤的欄位。

## 圖譜固定席

- **`lumos-cli-read` 等節點的 INVARIANT:**diff 新增獨立子命令 `security`,在 `main()` 的 `Env(vault)` 之前分流,沒碰 `search`、`contracts` 等既有路徑,不影響。
- **`_regular_own_fd` 加 `dir_fd=None`:**預設路徑與舊行為相同,不影響既有呼叫端。
- **`_visible_lines` 改用 `_fence_regions`:**我逐一核對。收尾標記行輸出與否、`keep_fenced` 時圍欄內標記行照輸出、未閉合最後一段,新舊行為一致,不影響。

最嚴重 severity: major,blocking 共 3 條(Finding 1 到 3)。
