severity: minor

審查範圍是修補差異和 `scripts/lumos` 的實際行為。我在臨時 git 目錄用 `cmd_dispatch_lens_spec` 實跑了提交寫法和工作樹寫法,臨時目錄已刪。後端卡 `be-api-compat`、`be-authz` 這次只有 CLI 與派工詞輸出,沒有對外端點,所以只走了輸出相容(見下)。

## 一般使用與白名單誤擋(已走過)

- 工作樹寫法的計劃,連結中文名、含半形空白名、`Issues/事故 一`、含半形括號名都照常附內容,固定席與落點也照列。
- 提交寫法(`<完整編號>:docs/x-knowledge/Projects/計劃_計劃.md`,計劃檔在別的工作樹時照用)同樣走得通,「只在提交裡」的節點與程式檔都列得出來。
- 用白名單掃本 repo `lens-repo` 的 `Systems`、`Issues`、`Projects` 共 571 篇節點:0 篇被擋,最長在 80 字內。節點名沒有誤擋。
- 白名單比舊的節點名字元集多收了括號,節點名這邊沒有退步。
- 提交裡存 NFD(日文濁音)的名字,現在查得到。ls-tree 關掉 precompose 後也能比到。
- 固定席過濾後,`pinned` 計數是過濾後的數字,「N 篇固定席節點名字不合或指到圖譜外面」那行也有印。候選上限、上限只算到一半的說明行也都對。
- 這些路徑上沒讀到 `_spec_commit_present` 回傳新形狀的漏改呼叫端:`scripts/lumos`、`scripts/hooks` 裡沒有別的呼叫點。
- `_nodehome_cat_sizes` 補 `ValueError` 是對的,該函式的行對齊也沒問題:候選已排除換行、NUL、空白字元。

## 輸出相容(`be-api-compat`)

`--json` 新增 `cands_truncated`,是加欄位,舊讀者看得懂。但 `scan_truncated` 的語意變寬了:候選超過上限時它也為真,之前只代表時間預算用完。消費者若把它等同「超時」,會讀錯。我沒在 `scripts` 裡找到這樣用它的程式。

## Finding

### 1. 計劃路徑改成白名單後,常見標點的合法檔名,來源行被誤印成「路徑含不收的字元」

severity: minor
blocking: 否 — 只影響「計劃來源」那一行的顯示,計劃內容照讀、固定席與連結不受影響。
引句:「_LENS_SPEC_PATH_SHOW_RE = re.compile(f"[{_LENS_SPEC_NAME_CHARS}]{{1,300}}")」
問題:原本計劃路徑只擋控制類字元和反引號。現在改用與節點名同一份字元白名單,`& + , ： 、 ' —` 這些合法檔名字元都不在裡面。
失敗情境:輸入 `<編號>:docs/x-knowledge/Projects/Q&A_計劃.md`、`Projects/設計審：二_計劃.md`、`Projects/a+b_計劃.md`,`_lens_spec_path_showable` 都回 False(我實跑確認)。來源行印成「提交 xxx 的(路徑含不收的字元)」,席位對不上 `spec-freeze` 印的那一行,而 `spec-freeze` 本身接受這些路徑。本 repo 的 `Projects` 目前沒有這類名字,消費專案可能有。
佐證:`scripts/lumos:49185`、`scripts/lumos:49201-49203`、`scripts/lumos:49572`

### 2. 計劃同時寫 NFC 與 NFD 兩種寫法連到同一篇節點(或同一支程式檔)時,結果重複列兩次

severity: minor
blocking: 否 — 只有計劃自己混用兩種正規化寫法才會觸發,是顯示重複。這個行為修補前就有,但這次「每個候選 NFC、NFD 都問」讓 NFD 儲存的物件也查得到,才能看到。
引句:「elif cidx[_ud.normalize("NFC", f"{vault_rel}{node}.md")]:」
問題:`cidx` 的鍵一律是 NFC,所以 `cidx` 本身沒有重複。但 `_lens_spec_linked` 的 `seen` 比的是原始字串,`_lens_spec_code_cands` 也是原始字串去重。NFC 與 NFD 兩個寫法各過一次,下游各 append 一個 NFC 名。
失敗情境:計劃寫 `[[Systems/ガイド]] [[Systems/ガイド]]`(第二個是 NFD),提交裡只有 NFD 物件、會談目錄沒有。輸出「- …Systems/ガイド.md [計劃連結]:只在那個提交裡…」出現兩行一樣的,「沒算牽連:scripts/ガイド.py, scripts/ガイド.py」也重複。程式檔那邊還會多吃一個 `_LENS_SPEC_MAX_FILES` 名額。我實跑確認。
佐證:`scripts/lumos:49641-49650`(`_lens_spec_linked`)、`scripts/lumos:49610-49612`(`_lens_spec_code_files`)

資料狀態五問:輸入形狀(NFC/NFD、空白、中文、`Issues/`)已走過。空值、`cidx=None` 與候選超過上限的 `get()` 回 None,下游一律「不列也不數」,沒讀到錯。超大輸入的上限和逾時路徑,我只讀程式,沒有另做實驗。

最高等級 minor,blocking 0 條。
