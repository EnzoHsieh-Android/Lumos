severity: major

## F1 改用 _json_at_ref 後,帶 BOM 的 .lumos/config.json 被當成「讀不懂」,宣告全丟
severity: major
blocking: 是
引句:「cfg = _json_at_ref(root, base, ".lumos/config.json")」
file: `scripts/lumos:30833`(_json_at_ref 直接 json.loads(r.stdout),不去 BOM)、diff 內 `_review_roles` 該行
場景:起點版本的 .lumos/config.json 以 UTF-8 BOM 開頭(Windows 編輯器常見),內容完全合法。舊碼 `raw.lstrip("﻿")` 容許;新碼 _json_at_ref 的 json.loads 對開頭 BOM 丟 JSONDecodeError(ValueError)→ 回 None → cat-file -e 說檔案在 → unreadable=True → 整份 review_roles 宣告不用,還印「讀不懂」警告。
重現(臨時目錄,BOM+合法宣告的 base 版本):
  python3 run.py(載入 worktree 的 scripts/lumos,呼叫 _review_roles(root, base, head))
  輸出:['.lumos/config.json 讀不懂,review_roles 這次不用'] {'api/a.py': 'backend'}   # 宣告 api/* → frontend 沒生效
r1 的 a7 修法把「容許 BOM」這個既有行為丟了(同檔 _node_flavor_of 還特地寫容許 BOM)。

## F2 工作樹 _node_flavor 改走 reader 後,最近的 package.json「讀不了」會往上找到父層,改判別的角色
severity: major
blocking: 是
引句:「_NODE_FLAVOR_CACHE[key] = p.read_text(encoding="utf-8") if p.is_file() else None」
file: `scripts/lumos:20478`(_node_pkg_text)、`scripts/lumos:20506`(_node_flavor_at 遇 None 就往上)
場景:monorepo,根 package.json 是後端(express),pkg/package.json 是前端(vue)但存成 UTF-16(或權限讀不了)。舊碼讀到最近那份卻解不了 → 回 None(docstring 寫明「最近那份讀得到卻解析不了 → None」)。新碼 _node_pkg_text 把 UnicodeDecodeError/OSError 也化成 None(等同「沒有這個檔」),_node_flavor_at 於是繼續往上讀根層 → 判成 "node"。前端檔拿到後端題,正是上一輪要防的事。git 版(_nodehome_cat_blobs 用 errors="replace")讀得到亂碼文字 → 解析失敗 → None,與工作樹版現在不一致。
重現(pkg/package.json = FF FE + utf-16le 的 {"dependencies":{"vue":"3"}},根 package.json 有 express):
  新碼 _node_flavor('pkg/a.ts', root) → node
  舊碼(c7f70335 版 scripts/lumos)同輸入 → None

## F3 起點設定為超深巢狀 JSON 時 RecursionError 逸出 _review_roles,整個角色計算靜默丟掉且沒警告
severity: minor
blocking: 否
引句:「cfg = _json_at_ref(root, base, ".lumos/config.json")」
file: `scripts/lumos:30833`(只 except ValueError)
場景:base 的 .lumos/config.json = "[" * 200000。_json_at_ref 丟 RecursionError,不被 `_review_roles` 接;兩個呼叫點的寬接把它吞成「沒有角色」,連「讀不懂」警告都沒有。重現:對該 repo 呼叫 _review_roles → RAISED <class 'RecursionError'>。測試 t_review_role_errors_never_break_dispatch_or_pitfalls 的「超深巢狀設定 → 當成讀不懂」那行只是直接傳 unreadable=True,並沒走到這條路,是空測。不拖垮派工(寬接生效),所以只算 minor。

## 已走過、判不影響的項目
- ls-tree -l -z 解析:含 tab 路徑用 partition 取第一個 tab、路徑正確;子模組 size 為 "-" 不是數字 → 照留,cat-file 回 commit 型 → None;symlink 為小 blob;含換行檔已在 wanted 階段排除;512K 界線是 `>` 故剛好等於仍讀。
- 掛鉤重叫:rc2 空輸出還有「不在 git 專案/範圍壞」等合法情境,會多跑一次同樣快速失敗的呼叫,成本可忽略,總時間仍受 _run_tmo≤cap 各自夾住;不算問題。
- cfg 存在且為 dict 時 `_cfg_there` 為 False,_lens_git 回 None(git 跑不起來)時 bool(None) 為 False,兩者皆不誤報。
- 圖譜鏡頭(LUMOS-IMPACT):固定席 design-loop / lumos-cli-lifecycle / pitfalls-code-loop 的 INVARIANT 與 RISK 行讀過,宣稱的是處置閘、re-inject 位元組保留與守衛面,本 diff 只動角色段與掛鉤重叫,不碰那些行為,判不影響。

總結:最嚴重 major;blocking 2 條
