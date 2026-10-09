severity: major

三個問題我都對照了現有程式碼。結論:結構大致對齊,但有兩條 major,都是專案已有功能卻另寫一套。

## 1. 分層與依賴方向

- 推送前風險分級沒有往圖譜層跨。`_arch_target_changed_files` 只在 `if _at_rules` 時才跑,不載圖譜,跟原本「推送前熱路徑不載圖譜」一致。
  - 引句:「_at_files = _arch_target_changed_files(repo_root, _at_base, _at_head) if _at_rules else []」
  - 對照:`scripts/lumos:41702`。
- 共用化沒有改變既有呼叫者的行為。`_lens_base_on_mainline` 抽出後,圖譜段仍是主線找不到就 `no_mainline`(rc 4)、起點不在主線就 `base_not_mainline`。`_json_at_ref` 其他 4 個呼叫者(`scripts/lumos:22423`、`26730`、`45494`、`45495`)都沒傳 `strict`,走原本的寬鬆解碼。`_review_roles_config` 改呼叫 `_config_glob_error` 後,判斷式逐字相同。
- 程式碼放法有兩處跟鄰居不同(ARC2-2 到 ARC2-4)。

ARC2-1
引句:「_ARCH_TARGET_CTRL_RE = re.compile(r"[\x00-\x1f\x7f]")」
既有碼:``scripts/lumos:34375`` 的 `_path_special_chars`(共用類別組 `_PATH_SPECIAL_CATS`)和 ``scripts/lumos:11254`` 的 `_esc_clean`。
說明:專案已有控制字元判斷與清洗。`_esc_clean` 的註解明說,只認 C0/DEL 會漏掉 U+2028/2029(`splitlines` 會在那裡切行)、C1、雙向覆寫和零寬字元(`scripts/lumos:34381` 附近)。新寫的正則加上 `_arch_target_text` 裡的內層 `cl()` 是第二套消毒,範圍比既有的窄。這支檔名消毒正是修補要防的注入路徑,所以漏洞留在原處沒被補上。
severity: major
blocking: 是

ARC2-2
引句:「def _arch_target_changed_files(root, base, head=None):」
既有碼:``scripts/lumos:26688`` 的 `_review_role_changed_files`。它的文件字串寫著「派工角色段與推送前分級那一行共用這一支」,同樣處理 `-M` 改名、`_vendored_skip`、`_PITFALL_DIFF_TEST_PAT` 和文件帳檔過濾。
說明:改動檔清單現在有三套來源。一是 `_review_role_changed_files`(name-status),二是新增的 `_arch_target_changed_files`(numstat -z),三是 pitfalls 裡 diff 文字解析出的 `added`。
- 同一支 pitfalls 函式裡,鄰居基準用 `added`,目標基準改用 `_at_files`,兩份清單口徑不同。
- 這支還新增了 `head=None` 代表工作目錄的語意,是既有清單函式沒有的。
- 修補只把「分級與派工鏡頭」兩處併成一支,沒有併進既有的角色清單函式。差別只在目標段要排除純刪除,可以在既有函式上過濾。
⚠ 這條是否算「專案已有同功能」要編排者判:既有函式把刪除檔也算進去,語意不完全相同。
severity: major
blocking: 是

## 2. 命名與錯誤處理

- `_arch_target_note_rules` 改走共用讀法,跟既有做法一致。它用 `_note_summary_entries`、`parse_rule_fields`、`_rule_stale_keys`,本機日期取法和 `scripts/lumos:3962` 相同。派工鏡頭用 `_note_from_text` 解析單篇,正是它文件字串寫的用途。
- 檔名消毒、`nfc`、`_vault_slug_of` 和 doctor 的 `ok(...)` 都已改成共用函式。
- 派工鏡頭失敗時附說明行,對照角色段的寬接(`scripts/lumos:46435`)。差別是目標段出錯會回說明、角色段回空字串。這是有意的,也寫進了 Issue。

ARC2-3
引句:「there = _lens_git(root, "cat-file", "-e", f"{ref}:.lumos/config.json")」
既有碼:``scripts/lumos:26730`` 到 ``26732``。`_review_roles` 同樣先讀 `_json_at_ref`、再用 `cat-file -e` 分辨「檔在但讀不懂」。
說明:同一份設定檔有兩處各自內嵌這段判斷,而且語意不同。
- `_review_roles`:讀不懂一律警告;git 失敗時靜默。
- `_arch_targets_at`:讀不懂只有原文提到 arch_targets 才警告;git 失敗一定警告。
修補說「讀法同 review_roles」,但只把 `strict` 加進了 `_json_at_ref`,沒有抽出共用讀法。
severity: minor
blocking: 否

ARC2-6(命名)
引句:「ml, _on_ml = _lens_base_on_mainline(root, base_sha)」
說明:區域變數加底線前綴,同一輪新寫的 `_dispatch_lens_arch_text` 裡卻是 `on_ml`。
另外 hook 把函式改名為 `_extra_text`,呼叫處變數仍叫 `_role = _extra_text(r)`(``scripts/hooks/claude/dispatch-lens-hook.py:476``),名稱和內容(角色加目標架構)對不上。
severity: minor
blocking: 否

## 3. 第二種做法

除了 ARC2-1、ARC2-2,還有三處:

ARC2-4
引句:「def _dispatch_lens_spec_with_arch(spec_path, repo=None, as_json=False):」
既有碼:合併 JSON 的尾段在 ``scripts/lumos:46369`` 到 ``46384``(`_cmd_dispatch_lens_impl`);設計審自己找圖譜資料夾的做法在 ``scripts/lumos:46726``。
說明:
- 外層包裝的形狀跟角色段一致(redirect_stdout、接在後面、另放 `arch_text`),這個方向對。
- 但合併 JSON 的尾段是 `_cmd_dispatch_lens_impl` 的近乎逐字複製。
- 包裝層重新算了 repo root 和計劃檔路徑。
- 找圖譜資料夾也另走一條:`_arch_target_vault_rel(root, "HEAD")` 用 `ls-tree`,設計審本體用工作目錄 glob,兩條來源並存。
severity: minor
blocking: 否

ARC2-5
引句:「        ml, on_ml = _lens_base_on_mainline(root, b)」
既有碼:``scripts/lumos:46435`` 的 `_dispatch_lens_role_text` 完全沒有主線檢查,仍讀範圍起點那一版的 `review_roles`。
說明:同一次派工、同一份 `.lumos/config.json`,角色段信起點版,目標段只信主線起點,兩套信任規則並存。Issue 筆記已明文記錄這個落差,我判為已知且有意的不一致,只列出來。
severity: minor
blocking: 否

## 沒有舊的平行實作留下的項目

- `_arch_target_rules`、`_ns_summary_logical`、`slot_parse` 的舊路徑都已刪除。
- `unicodedata.normalize` 已統一成 `nfc`。
- doctor 的手工印出已改用 `ok`。
- `cmd_dispatch_lens_spec` 的 `arch_target` 參數已移除,簽名回到原樣。

不對齊共 6 條,其中 major 2 條

總結最嚴重 severity: major
