severity: major

## F1 用 ls-tree -l 另查一次 git 內檔案大小(第二種做法)
severity: major
blocking: 是
引句:「r = _lens_git(root, "ls-tree", "-l", "-z", ref, "--", *paths)」
說明:專案裡沒有任何地方用 `ls-tree -l` 問 blob 大小。既有的 ls-tree 都只取名單(`--name-only`)或只確認路徑存在;要讀內容就走 `_nodehome_cat_blobs` 一次 `cat-file --batch` 讀完,且該函式 docstring 明講「成本在開 git 行程」。這裡先多開一個(每個版本一個)ls-tree 行程量大小,再開 cat-file 讀內容,是「另一種查檔案大小」加上兩趟讀取;讀完後又用 `v[:_ROLE_MAX_BYTES]` 再截一次,同一個上限兩處各守一次。工作樹的大小檢查則用 `stat().st_size`。對照:file: `scripts/lumos:25226`(ls-tree 只取名單)、file: `scripts/lumos:23336`(_nodehome_cat_blobs 批次讀取)、file: `scripts/lumos:1784`(stat().st_size 量大小)。若要對齊,宜把大小限制放進批次讀取那一層(例如 cat-file --batch-check 或讀取端截斷),不另開一條路。

## F2 掛鉤新增「拿掉旗標重叫一次」的重試(專案裡沒有的做法)
severity: minor
blocking: 否
引句:「新掛鉤配舊 lumos:舊版不認 --role-cards 會回 rc2 空輸出,不重叫的話連圖譜段都丟」
說明:⚠ 判不準交編排者。其他 hook 對子行程失敗一律「`_debug` 一行 + 放行」,沒有任何 hook 會重跑子行程;這裡是第一個重試,且重試分支本身沒有 `_debug` 記一筆(其他失敗分支都有記,見 file: `scripts/hooks/claude/dispatch-lens-hook.py:268`、`:374`)。因為沒有既有的重試可以比較,不算「第二種」,但錯誤處理/日誌與鄰居不一致。另外它靠 `returncode == 2 and stdout 為空` 推斷「舊版不認旗標」,與其他分支用 rc 5 表示超時的慣例(file: `scripts/hooks/claude/dispatch-lens-hook.py:261`)不同類,屬推斷式判斷。

## F3 兩處新加的寬 except Exception 且不留日誌
severity: minor
blocking: 否
引句:「except Exception:
            _rr = None」
說明:pitfalls 那處與 dispatch 那處(`role_text = ""`)都是吞掉全部例外、什麼也不記。鄰居寬接的做法:`_stack_questions_config` 的 `except Exception as e` 會把 `e.__class__.__name__` 放進警告(file: `scripts/lumos:20773-20774`);hook 端的寬接都配 `_debug`。這裡兩處連例外類別都沒留,出錯時使用者只看到「角色行消失」,無從得知。dispatch 那處有註解說明是刻意的,該處理由成立,pitfalls 處註解則只寫「同派工那邊」。建議至少比照鄰居留一句含類別名的提示。

## F4 設定警告改成不回填值、且兩條路徑印法不同
severity: minor
blocking: 否
引句:「print(f"提醒:{_w}", file=sys.stderr)   # 照棧別題組設定警告的印法」
說明:pitfalls 路徑改印 stderr「提醒:」,對齊 file: `scripts/lumos:4247` 的做法,這部分一致。但(a)註解說「照棧別題組設定警告」,而 `_stack_questions_config` 的警告會回填 `{g!r}`、`{t!r}` 與例外類別名(file: `scripts/lumos:20781`、`:20786`),新警告刻意不回填,與鄰居寫法不同(理由——角色段放框外、防注入——成立,列出僅供留意);(b)同一份警告在 dispatch 路徑仍以 `(角色鏡頭)⚠` 進派工詞,兩個出口格式不同,但通道不同(給人看 vs 給審查員),可接受。另 `_review_roles_config` 改吃 `_json_at_ref` 的結果後,原本的 `lstrip("﻿")` 容許 BOM 消失(`_json_at_ref` 不處理 BOM;`_node_flavor_of` 仍處理),兩處對 BOM 的容忍不一致,⚠ 交編排者判是否要緊。

## 三問
1. 分層與依賴方向:未見跨層直呼。新程式碼都走 `_lens_git`、`_json_at_ref`、`_nodehome_cat_blobs` 這些既有 helper;`_node_flavor` 改成統一走 reader(工作樹版由新的 `_node_pkg_text` 提供),反而拿掉原本工作樹/版本兩條平行路徑,方向是收斂的(對照 file: `scripts/lumos:20469`、`:20506`)。`_review_roles_config` 改吃已解析的內容並複用 `_json_at_ref`(file: `scripts/lumos:30833`),與「只信 base 設定」的既有讀法一致;存在性判斷用 `cat-file -e`,與 `_path_at_pin` 同形(file: `scripts/lumos:20231`)。
2. 命名與錯誤處理:命名(`_role_budget`、`_ROLE_MAX_BYTES`、`_review_role_small_enough`)與鄰居一致。錯誤處理見 F2、F3、F4:重試無日誌、寬 except 無日誌、警告不回填值與鄰居寫法略有落差。`_node_flavor_of` 補 `RecursionError` 屬窄化補洞,與 `except ValueError` 同形,無問題。
3. 第二種做法:F1(ls-tree -l 量 git 內檔案大小,另加第二趟行程)是本輪唯一的第二種做法。快取方面,`_node_pkg_text` 沿用 `_NODE_FLAVOR_CACHE`(改以檔為鍵),沒有新增快取機制;重試方面見 F2,無既有重試可比,不計為第二種。

總結:不對齊共 4 條,其中 major 1 條。
