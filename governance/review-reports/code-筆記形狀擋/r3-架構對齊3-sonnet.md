severity: clean

## 驗收 r2 兩條修法

**①找主線改用既有 `_mainline_ref` 加 `remote_only` 參數**:確認正確。`_mainline_ref` 定義在
`scripts/lumos:28070`,r3 只加了 `remote_only=False` 參數(預設候選不變,`remote_only=True` 時只留
`main@{upstream}`、`master@{upstream}` 兩項)。`_ns_mainline_refs`(`scripts/lumos:23547`)改成
`_mainline_ref(repo_root, remote_only=True)`,不再自己找遠端 HEAD。且 `_mainline_ref` 既有呼叫端
(`scripts/lumos:28943`、`29812`、`30691`,皆用預設 `remote_only=False`)行為沒被動到。沒有另開一支函式。

**②`[src:]` 正則改用既有 `SRC_REF_RE`**:確認正確。`SRC_REF_RE`(`scripts/lumos:4283`)本來就給
Check J / regen 邏輯用(`scripts/lumos:4593`、`4614`)。`_ns_check_line` 這輪把私有的
`_NS_SRC_MARK_RE = re.compile(r"\[src:[^\]]*\]")` 整支刪掉,改成 `SRC_REF_RE.sub(" ", text)`
(`scripts/lumos:23658`),沒有殘留第二份正則。

## 逐題

1. **分層與依賴方向**:乾淨。這輪新加的 `_ns_exclusions`、`_ns_range_added` 裡的 `_renames`/`_carry`
   都是 note-shape(`_ns_*`)呼叫既有的共用低層(`_lens_git`、`_nodehome_git`、`_nodehome_name_status`、
   `_mainline_ref`),方向跟原本一致——沒有看到相反方向(nodehome 或 lens 反過來呼叫 `_ns_*`)。

2. **命名與錯誤處理**:跟同檔鄰居一致。
   - `_ns_exclusions` 內 `_lens_git(repo_root, "merge-base", "--is-ancestor", tip, ref)` 這個寫法
     跟 `_nodehome_golive`(`scripts/lumos:22946/22951`)、doctor 事後掃描(`scripts/lumos:23872/23884`)、
     甚至另一支鏡頭指令(`scripts/lumos:28947`,同樣接在 `_mainline_ref` 之後判「base 在不在主線上」)
     用的是同一個慣用語:呼叫、檢查 `r is not None and r.returncode == ...`。git 失敗(`r is None`)時
     `_ns_exclusions` 不排除該 ref(等於「查更多」),跟 PRIOR-ART 寫的「找不到主線就不排除任何提交」一致。
   - `_renames` 回 `None`(git 失敗)、呼叫端立刻 `if ren is None: return None` 往上傳,跟 `_ns_diff`/
     `_ns_git` 現有的「失敗回 None、逐層 propagate」慣例完全一樣。
   - `by_name` 的惰性快取(`_name_cache`,`scripts/lumos:23738`)跟既有 `refs_now`/`refs_cache`
     closure(`scripts/lumos:22986-22990`,同檔 nodehome 那段)是同一個形狀:`if x not in cache:
     cache[x]=compute(); return cache[x]`,不是新發明的快取寫法。

3. **第二種做法**:沒找到。
   - 改名偵測用的是既有 `_nodehome_name_status`(`scripts/lumos:22723`),`_renames` 只是包一層取
     `[1]`(新路徑→舊路徑)那個既有欄位,不是另寫一支改名判斷。
   - 合併新增行沿用既有 `_merge_new_lines`/`_nodehome_merge_wrote_new_lines` 拆法(這輪沒再動這支)。
   - CI 與 doctor 給消費專案的「建本地 main 追蹤 origin/main」是 workflow YAML 裡的一行 shell
     (`git show-ref -q --verify refs/heads/main || git branch --track main origin/main || true`,
     `.github/workflows/ci.yml:132`),純粹是為了讓 `_mainline_ref` 的 `main@{upstream}` 在 CI 環境
     解析得到,不是重寫既有邏輯的第二份;repo 裡沒有其他地方已經在做同一件事,所以不算「另寫一份」。

引句:「沿用既有主線判定 _mainline_ref,只認已推上去的 upstream」
引句:「只在帶 regen 的筆記的 summary 歸重建守衛(Check J)驗」

對照:`scripts/lumos:28070`(`_mainline_ref` 定義,`remote_only` 參數)、`scripts/lumos:4283`
(`SRC_REF_RE` 定義)、`scripts/lumos:22723`(`_nodehome_name_status` 定義)、`scripts/lumos:22986`
(既有 `refs_now`/`refs_cache` 惰性快取寫法)、`scripts/lumos:28947`(另一支鏡頭同樣用
`_mainline_ref` + `merge-base --is-ancestor` 判主線可達)。

沒有 major 或 minor 發現。
