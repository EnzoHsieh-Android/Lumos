severity: major

這一輪沒有發現能讀到 vault 外的路徑,也沒有發現寫入、執行外部指令或寫入密鑰的路徑。
- 唯讀:`cmd_security_list` 在分派時不經過 `Env(vault)`,整條路徑沒有寫檔、起子程序或連網。
- 捷徑與名稱競態:逐層 `O_NOFOLLOW|O_DIRECTORY` 加 `dir_fd` 開檔,列舉到的捷徑與特殊檔都列錯誤,開檔後會判一般檔。
- 路徑繞過:`_secinv_node_rel` 擋絕對路徑、`..`、空段與反斜線,不會開檔。
- 撞名:交給 `Env.from_texts` 前先查 NFC 撞名。
- 讀前讀後比對:會比對屬性並重列目錄。

## F1:有標籤的 Systems 節點放一個空登記塊,就從「未登記」缺口清單消失

severity: major
blocking: 是

攻擊路徑:
- 誰:使用者本人,或照常操作、先放骨架登記塊再補條目的 AI。
- 從哪:編輯一篇帶 `tags: flag/security-relevant` 的 Systems 筆記。
- 送什麼:加一塊 `lumos-security-v1`,內容是 `{"schema_version":1,"controls":[]}`。
- 拿到什麼:`unregistered_nodes` 不再列這篇,退出 0、`errors` 為空、`read_complete` 為 true。只要同庫另有一條合法登記,`registration_complete` 也是 true。

我造了暫時圖譜實跑確認:`a.md` 有標籤加空塊,`b.md` 有標籤沒有塊。輸出 `unregistered_nodes` 只有 `['Systems/b.md']`,`a.md` 被藏掉。

原因是程式用「這篇有沒有合格的塊」判斷已登記:`block_nodes.add(rel)` 在 `_secinv_collect`,過濾在 `_secinv_build` 的 `rel not in block_nodes`。計劃寫的是「標籤精確為 flag/security-relevant 但沒有條目的節點列 unregistered_nodes」。程式把「有塊」當成「有條目」,所以只要有塊,不管裡面有沒有條目,都被算成已登記。

引句:「"unregistered_nodes": [rel for rel, n in env.notes.items()」

file: `scripts/lumos:7279`(`if "flag/security-relevant" in as_list(n.fields.get("tags")) and rel not in block_nodes`)

file: `docs/lumos-toolchain-knowledge/Projects/資安護欄唯讀盤點_計劃.md:93`

## F2:登記內容原樣帶進給 AI 的輸出,沒有長度上限也沒有資料框,JSON 模式不跳脫雙向控制符

severity: minor
blocking: 否

攻擊路徑:
- 誰:第三方寫的消費專案圖譜(使用者 clone 下來的),後面由 AI 讀輸出。
- 從哪:`lumos security list --json`,或文字模式。
- 送什麼:登記塊的 `abuse_case`、`status_reason` 等自由欄位帶祈使句;或故意寫壞的塊,用很長的未知欄位名,其中控制項層級的 `"、".join(extra)` 沒有截斷。
- 拿到什麼:指令句進到 AI 的上下文。

文字模式有用 `_kill_esc` 跳脫控制字元,但跳脫的類別只有 `Cc/Cf/Zl/Zp/Cs`,內容不截斷、也沒有「以下是資料,不是指令」的圍欄。JSON 模式用 `ensure_ascii=False`,雙向控制符與 U+2028 會原樣輸出。因為筆記本來就會被 AI 用 `lumos show` 讀,新增的曝險有限,只算縱深防禦。

引句:「probs.append(f"{name} 有未列出的欄位 " + "、".join(extra))」

file: `scripts/lumos:7357`(`_secinv_show`,文字模式的輸出出口)

## F3:圖譜根目錄會跟隨捷徑,自動找圖譜時被指到任意目錄

severity: minor
blocking: 否

攻擊路徑:
- 誰:在不可信 repo 裡執行 `lumos security list` 的使用者或 AI。
- 從哪:不帶 `--vault`,由 `_secinv_select_vault` 自動找。
- 送什麼:repo 內的 `docs/x-knowledge` 是指向 repo 外目錄的捷徑。
- 拿到什麼:`s.is_dir()` 與根目錄的 `os.open(str(vault), O_RDONLY|O_DIRECTORY)` 都跟隨捷徑,所以會讀 repo 外目錄裡的 `.md`。

能讀到的只有含 `lumos-security-v1` 的檔,洩漏面很窄,但與「不跟捷徑」的宣稱不一致。

引句:「cands += [s for s in sorted(docs.iterdir()) if s.is_dir() and s.name.endswith("-knowledge")]」

## F4:空圖譜、零登記、覆蓋未知都退出 0,`registration_complete` 在覆蓋未知時仍可為 true

severity: minor
blocking: 否

攻擊路徑:
- 誰:用退出碼判斷通過的自動化,或照常操作的 AI。
- 從哪:`lumos security list --vault <錯指的目錄>`;或有登記但沒寫 `inventory` 的圖譜。
- 送什麼:`--vault` 指到一個沒有任何圖譜內容的目錄,或圖譜裡有合法登記但缺 `inventory`。
- 拿到什麼:前者退出 0,`read_complete` 為 true,`errors` 為空,只靠 `registration_complete:false` 與一句提示說明沒有登記。後者 `registration_complete` 為 true,但 `coverage.status` 是 unknown。

計劃已決定零登記退出 0,有提示文字,所以只算縱深。`--vault` 只檢查 `is_dir()`,不檢查是不是圖譜。

引句:「return 0 if rep["read_complete"] and not rep["errors"] else 2」

file: `scripts/lumos:7295`(`registration_complete` 的計算;`_secinv_exit_code` 在 `_secinv_build` 之後)

最嚴重 severity:major,blocking 共 1 條。
