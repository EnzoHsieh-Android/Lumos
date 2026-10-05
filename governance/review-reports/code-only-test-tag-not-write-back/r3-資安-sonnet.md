severity: major

# 第 3 輪資安審查(攻擊者視角)

## 1. 不可信輸入流到危險操作
綁定名稱流向:`_nodehome_strip_test_tags` 拿出名稱,進 `_NsTrJudge`,再進 `_test_in_tree` 的 `git grep`。看過的結果:
- `git grep` 用 list 參數(沒有 shell),名稱前有 `-e`、整字固定字串(`-w -F`),所以沒有 shell 插值、沒有正則注入、名稱不會被當成選項。
- 名稱先過 `_NODEHOME_TEST_TAG_VALUE_RE`(白名單字元),`_plat` 又擋 `[]`。
- 路徑跳脫:pathspec 只由 `.lumos/config.json` 的平台根組成,不由名稱組成,而且 `relative_to(repo)` 會擋到 repo 外。這是既有碼,這輪沒新增攻擊面。

已看,無執行類的洞。名稱的字元白名單偏寬,下面這一條就是它造成的。

引句:「r = _sp.run(["git", "grep", "-w", "-F", "-q", "-e", name, at_sha, "--", *_spec],」
file: `scripts/lumos:44482`

## 2. 權限與守衛繞過
severity: major
blocking: 是(判準:可直接利用、繞過這輪要補的守衛,而且我當場重現過)

- 誰:能改筆記的貢獻者,也就是消費專案裡不受信任的人。
- 從哪裡:Systems 筆記的摘要或正文。
- 送什麼進來:在節點裡加一個 `[test:<英文句子>.<真測試名>]`。句子只用英數、空白、句點。例:`[test:This sentence explains why the gate was changed.t_nodehome_test_tag_strip_edges]`。
- 為什麼會過,三道關各放一次:
  1. `_NODEHOME_TEST_TAG_VALUE_RE` 允許空白與句點,所以整段值被當成「像測試名」而被拿掉、不計入內容。
  2. `_classify_test_refs` 的 `_KILL_METHOD_OK_RE` 第二個分支 `^[\w .]+$` 放行任意英文句子。它再以 `method.rsplit(".", 1)[-1]` 取最後一段,只要最後一段是真測試就判 real。
  3. 推送時 `_NsTrJudge._judge` 傳給 `_test_in_tree` 的也只是最後一段,`git grep` 找得到,於是判 yes。
- 拿到什麼:`j(nm)[0] == "yes"`,`_nodehome_tag_only_change` 回 True。一段 200 字內的英文說明就藏在「綁定」裡,這篇節點被判成「只換測試綁定,沒寫說明」。
- 實測:我在 `/Users/enzo/harness/lumos-rtb3` 載入 `scripts/lumos`,對 `This sentence explains why the gate was changed.t_nodehome_test_tag_strip_edges` 跑 `_ns_tr_judge`,提交時(tip=None)與推送時(tip=HEAD 完整 sha)都回 `('yes', '')`。同一句交給 `_nodehome_strip_test_tags`,整段被當綁定拿掉。
- 這就是第 1 輪的「英文句子藏進綁定」,換成「類別.方法」的形狀再來一次。你們要求的「新名稱必須指得到真測試」只驗到最後一段,前面整段不驗。
- 建議(不改檔,只給方向):`_nodehome_tag_only_change` 對每個新名稱另外要求整串 fullmatch `[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*`(名稱本身不含空白),Kotlin 反引號名稱要單獨處理。或者拿整串名稱去核對 `methods_for`,不要退到最後一段。

引句:「j = judge() if judge else None
+        if j is None or j(nm)[0] != "yes":」
file: `scripts/lumos:43466`

另一條攻擊路徑「新增一支名字是一句話的測試來合法化說明」:`discover_test_methods` 認的是 IDENT 形狀的函式名,所以名字最多是 snake_case 長名,不是自由文字;Kotlin 反引號名稱可以含空白。這條要靠貢獻者真的提交一支測試,而且那支測試在審查中看得到,我只算推論。

severity: minor
blocking: 否(判準:推論,要貢獻者真的提交一支以句子命名的 Kotlin 測試,縱深防禦)

引句:「if len(v) >= 2 and v[0] == v[-1] == "`" and v.count("`") == 2:」
file: `scripts/lumos:26880`

其餘守衛看過:
- `_ns_tr_guard` 的簽出分支、`.lumos/config.json` 改動、已追蹤測試檔 M/D 三項,在推送時都讓 `_nodehome_tag_judge` 回 None,等於不豁免,方向是對的。
- 未追蹤的新測試檔不會被 `_ns_tr_guard` 看到,但第②道的 `git grep` 只查被推的版本,所以未提交的測試冒充不了。已看,無。
- 例外與逾時一律走不豁免:`except Exception: return None`,`skip` 與 `undecidable` 都不是 `yes`。這是 fail-closed,已看,無。
- `test-gone` 名稱必須出現在上一版的 `[test:]` 裡,所以不能憑空新增。已看,無。

## 3. 密鑰與個資
已看,無。這輪新增碼不讀也不印密鑰或個資。

引句:「return None」(在 `_nodehome_tag_judge` 的 `except Exception:` 之後,不外洩例外內容)

## 4. 加密與傳輸
已看,無。沒有網路、加密或傳輸相關的碼。

引句:「_nodehome_tag_judge(root, None if staged else tip_where)」

## 5. 執行邊界
已看,無新增的危險執行。`subprocess` 全是 list 形式,沒有 `shell=True`,沒有 eval/exec,沒有反序列化。`_lens_git` 與 `git grep` 都有逾時。

引句:「_NS_TR_GREP_CAP if left is None else max(0.1, min(_NS_TR_GREP_CAP, left))」

## 6. 行動端與新依賴
已看,無。這輪沒有行動端碼,也沒有新依賴(只用標準庫)。

引句:「import subprocess as _sp」

總結:全份最高等級 major
