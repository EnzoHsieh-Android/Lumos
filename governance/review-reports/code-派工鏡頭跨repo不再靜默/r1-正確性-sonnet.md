severity: minor

我先 clone 了 repo，新增的 `t_dispatch_lens_fail_reason_json` 等 5 支測試都綠。派工詞尾端我沒有看到「lumos 自動附加」，也沒有看到「圖譜沒有釘到節點」段。派工詞只有題目裡那段機械反查，三格皆空，不是圖譜節點，所以圖譜鏡頭沒有固定席可逐條答。從 diff 看，被注入的規則來自 `Projects/派工鏡頭注入_計劃` 與 `Systems/codex-harness` 的文字改動，沒有被動到合約行。角色鏡頭有附卡，下面有分析。

## F1 掛鉤把未驗證的範圍字串原樣放進說明，還包在反引號裡
severity: minor
blocking: 否
引句:「"或派工前在目標專案跑 `lumos impact --diff {what}`,把固定席內容貼進派工詞。照派工詞審查即可。")」
佐證: ``scripts/hooks/claude/dispatch-lens-hook.py: `MARKER_RE = ^LUMOS-IMPACT:\s*(\S+)\s*$` 只做 \S+，掛鉤自己沒驗範圍``；``scripts/lumos: `_lens_range_ok:44034` 只擋 -開頭、...、空白、非恰好一個 ..，沒擋反引號、$()、; 這類字元``

失敗場景：
1. 會談開在非 git 目錄，派工詞標記寫 ``LUMOS-IMPACT: x`id`$(id)..HEAD``。
2. lumos 在 `_dispatch_lens_graph` 先過 `_lens_range_ok`，再在 rev-parse 失敗後回 `not_git`。
3. 掛鉤走到 `FAIL_NOTE.format(what=rng, ...)`，`what` 沒有長度截斷，也沒有字元白名單。
4. 結果是派工詞尾端出現「請跑 `lumos impact --diff x`id`$(id)..HEAD`」，審查子代理可能照著執行。

repo 路徑有截 300 字並去換行，`what` 沒有，兩者處理不對稱。標記本來就是派工者自己寫的，所以沒有權限升級，只是說明行不是「固定字彙加已驗證欄位」。我沒有跑通這條路徑：本機掛鉤找不到可信的 lumos 就放行，沒有輸出，所以標「未能重現」並維持 minor。建議：`what` 加 `[:300]`，並要求符合保守的 ref 字元集，不符就不附繞法那句。

## F2 同一族的靜默放空還剩 `找不到主線` 與 `sha 解析不到` 兩條
severity: minor
blocking: 否
引句:「return _dispatch_lens_fail(as_json, "base_not_mainline", 4)」
佐證: ``scripts/lumos: `_dispatch_lens_graph` 的 print("擋下:找不到主線(main/master 都沒有)") 後仍 return 4，沒經 _dispatch_lens_fail``

失敗場景：
- 會談專案 A 的預設分支叫 `develop` 或 `trunk`，沒有 main 或 master。
- 掛鉤收到 rc4、stdout 空，`_lens_fail_why` 回 None，`_fail_note` 回空字串，派工詞原樣放行。
- 這就是「跨 repo 靜默放空」同一現象，只是改成 `ml is None` 這條路。
- `base_sha`/`head_sha` 解析失敗（rc2）也一樣。
- 這些原因代碼不在 `LENS_FAIL_REASONS` 內，屬設計取捨。若計劃沒寫「刻意只管三種」，建議補一個代碼或在計劃記為已知殘留。

## 查過沒問題
- 呼叫者與快取：`_dispatch_lens_graph` 的外部呼叫者只有 `_cmd_dispatch_lens_impl` 兩處。
  - Codex 武裝 `--arm` 會把 stdout 收進 buf，`rc != 0` 直接回傳，buf 丟棄。
  - 背景暖機的 stdout 是 DEVNULL。
  - 三條失敗路徑都在快取讀寫之前就 return，所以多印的一行 JSON 不會被當成功結果解析或寫進快取。
  - 引句:「print(_json.dumps({"lens_fail": code}))」
- 角色卡包裝：`role_text` 非空時，`_cmd_dispatch_lens_impl` 會 `json.loads` 最後一行，把 `role_text` 併進同一個 dict 後重印，所以 `lens_fail` 與 `role_text` 同時存在，說明在前、角色卡在後。
  - `role_text` 為空時（not_git 與 commit_missing 都是這樣，因為 `_dispatch_lens_role_text` 解不出 sha 就回空字串），原輸出照寫。
  - 引句:「_emit_updated(tool_input, prompt, "\n\n".join(x for x in (_note, _role) if x))」
- 舊 lumos 配新掛鉤：舊 lumos 不印 `lens_fail`，掛鉤得 None 後走原本只附角色卡或放行的路。
  - 新 lumos 配舊掛鉤：舊掛鉤會把 `{"lens_fail":...}` 當成 `lock_status` 解析，其中的 `spawn_error` 與 `lock_error` 判斷都是假，之後走 `rc != 0` 分支，只是照舊靜默，沒有誤判。
  - `--role-cards` 的退路條件需要 stdout 為空；新 lumos 在 rc2 時 stdout 非空，不會誤重叫。
  - 引句:「code = d.get("lens_fail") if isinstance(d, dict) else None」
- 值的型別：`lens_fail` 是 list、dict、數字、未知字串、最後一行不是物件，都落在 None，因為 `isinstance(code, str)` 在 `.get` 查表之前。stdout 多行只取最後一行。
  - 引句:「return LENS_FAIL_REASONS.get(code) if isinstance(code, str) else None」
- 路徑含換行：repo 路徑已去 `\n`、`\r` 並截 300 字，其他空白字元不處理，但不影響單行格式（測試也有驗）。
  - 引句:「repo=str(repo)[:300].replace("\n", " ").replace("\r", " ")」
- 範圍格式不合法與不帶 `--json`：回傳碼不變、不印 `lens_fail`，測試涵蓋。
  - 引句:「return _dispatch_lens_fail(as_json, "not_git", 2)」

總結:最高等級 minor(F1 是範圍字串未驗證就進派工詞,F2 是同族殘留的靜默路徑;沒有阻擋級的發現)
