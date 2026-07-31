---
type: verification
status: pass
feature: Task 9——CLAUDE.md 注入裁定第三次變更:有完整版 LUMOS:GRAPH-DISCIPLINE 區塊就整段策展取代(原地換位置)、位元組級備份(base64 藏在精簡版區塊自己的 HTML 註解裡)、uninstall 可精確還原
commit: TBD(本檔寫於 commit 前,寫完後補;見 task-9-report.md)
date: 2026-07-31
valid_under:
  - "install.sh/uninstall.sh 對完整版 sentinel 的判定仍是前綴匹配 `<!-- LUMOS:GRAPH-DISCIPLINE:START` + 完整匹配 `<!-- LUMOS:GRAPH-DISCIPLINE:END -->`(與 scripts/lumos 的 _CLAUDE_START_PREFIX/_CLAUDE_END 同款,未改版)"
  - "備份格式仍是 base64 藏在 `<!-- LUMOS-SLIM:FULL-BACKUP:BASE64:... -->` 這個固定字面樣式的 HTML 註解裡"
  - "slim/claude-block.md 仍含 `<!-- LUMOS-SLIM:FULL-BACKUP:NONE -->` 佔位符供 install.sh 字面替換"
revalidate_when:
  - "scripts/lumos 的 LUMOS:GRAPH-DISCIPLINE sentinel 格式/版本戳規則改變(_CLAUDE_START_PREFIX/_CLAUDE_END 定義變動)"
  - "slim/claude-block.md 改版但 FULL-BACKUP 佔位符字面樣式跟著換,install.sh/uninstall.sh 未同步更新"
  - "有人手動編輯已安裝的 CLAUDE.md 裡的 LUMOS-SLIM 區塊(破壞 base64 完整性),uninstall 行為未定義"
tags:
  - type/verification
  - status/pass
---
# 2026-07-31_slim-claude-md第三次裁定取代與備份還原

## 變更範圍

`docs/lumos-toolchain-knowledge/Projects/公開精簡版_計劃.md` 使用者對 [S3] 做出第三次裁定:「整段移除完整版區塊,但不該丟的不要丟——把仍然有效的內容吸收進精簡版區塊,只拿掉指向不存在指令的部分」。落地到三個檔案:

1. **`slim/claude-block.md`(新檔,61 行)**——策展後的精簡版紀律區塊靜態範本,取代 Task 8 版寫死在 `install.sh` 裡的 heredoc。內容吸收完整版裡仍然有效的部分(核心原則/進場三步/summary 符號表/合約鏈/可逆性標記/regen 重生標記/frontmatter 欄位),拿掉依賴已移除指令(`design-loop`/`code-loop`/`core-knowledge`/`pitfalls`/`spec-trace`/`signoff`/`init`/`update`)才有意義的段落。
2. **`slim/install.sh`**——CLAUDE.md 注入邏輯全面重寫:偵測完整版 `LUMOS:GRAPH-DISCIPLINE` sentinel(前綴匹配,含版本戳)→ 有就先 base64 編碼備份原文、原地整段換成精簡版區塊;沒有就插在檔首「# 標題」之後(沒標題插最前面);兩者都沒有(冪等重跑)就沿用既有精簡版區塊的備份標記,不重新編碼。
3. **`slim/uninstall.sh`**——對稱重寫:讀出精簡版區塊內建的 `FULL-BACKUP` 標記,是 BASE64 就解碼還原完整版原文回原位置,是 NONE 就單純移除精簡版區塊;其餘邏輯(sha256 比對全域指令、skill 目錄備份)不變。

`scripts/slim-gen.py` 組包清單加入 `claude-block.md`(吸取上一輪漏 `get.sh`/`uninstall.sh` 的教訓,新增檔案當下就同步補)。`slim/README.md` 的〈會不會動我專案的 CLAUDE.md〉整節重寫,記錄三次裁定演進與已知風險(完整版若自稱自動更新,其他人跑更新流程會裝回來,兩邊來回覆蓋)。

## 測試項目

### 1. 有完整版區塊 → install 原地取代 + 備份可精確解碼

| 步驟 | 預期 | 結果 |
|------|------|------|
| 造含完整版 sentinel 的 CLAUDE.md,跑 install.sh | 完整版區塊消失、精簡版區塊在原位置、區塊前後既有內容 byte-equal | ✅ |
| base64 解碼備份標記 | 與完整版原文(含其自己的 sentinel)逐位元組相同 | ✅ |

`t_slim_install_replaces_full_discipline_block_in_place`

### 2. uninstall 位元組級還原

| 步驟 | 預期 | 結果 |
|------|------|------|
| 承上,跑 uninstall.sh | CLAUDE.md 與安裝前完全 byte-equal(含完整版原文一字不差) | ✅ |

`t_slim_uninstall_removes_claude_md_block` 情境三

### 3. 冪等 × 備份不漂移

| 步驟 | 預期 | 結果 |
|------|------|------|
| 有完整版區塊時裝一次,再帶 `--force` 重裝一次 | 兩次跑完 CLAUDE.md byte-equal(備份沒被重新編碼、沒被洗成 NONE) | ✅ |
| 重跑兩次後再卸載 | 仍可正確 base64 解碼還原 | ✅ |

`t_slim_install_backup_survives_idempotent_reinstall`

### 4. 沒有完整版區塊 → 插檔首標題後

| 步驟 | 預期 | 結果 |
|------|------|------|
| 一般 CLAUDE.md(無完整版 sentinel),跑 install.sh | 精簡版區塊插在檔首 `# 標題` 之後(不是檔尾),既有內容 byte-equal | ✅ |

`t_slim_install_no_project_touch`(本輪換斷言形狀:原斷言插檔尾,改斷言插檔首)

### 5. 策展正確性

| 步驟 | 預期 | 結果 |
|------|------|------|
| 讀 `slim/claude-block.md` | 不含 `design-loop`/`code-loop`/`core-knowledge`/`pitfalls`/`spec-trace`/`signoff`/`lumos init`/`lumos update` 字串 | ✅ |
| 同上 | 含 `★INVARIANT★`/`★DEBT★`/`[test:`/`FLOW:`/`KEY:`/`valid_under`/`佚失:` | ✅ |
| `slim-scan.py` 掃 `claude-block.md` | 0 候選(無懸空引用) | ✅ |

`t_slim_claude_block_curation`

## 測試方式

`python3 scripts/test_lumos.py -k slim`——187 checks 全綠(含既有 t_slim_gate/t_slim_readme_assertions/t_slim_skill_reference_scan_assertions 等既有守衛,本輪未破壞)。★測試過程中發現並修正一個既有測試 bug★:`_slim_make_pkg_at` 系列測試(`t_slim_uninstall_backs_up_and_preserves_custom_files`/`t_slim_uninstall_refuses_foreign_bin`/`t_slim_uninstall_idempotent_second_run`/`t_slim_get_idempotent`)呼叫 `install.sh`/`get.sh` 時沒設 `cwd`,在舊版(檔尾 append-only、不判斷完整版區塊)行為下無害,但換成本輪的「偵測完整版區塊」邏輯後,若不設 `cwd` 會實際操作到跑測試當下的工作目錄——若那剛好是本 repo 根目錄,會真的去改動本 repo 自己的 `CLAUDE.md`(它同時有完整版與遺留的舊格式精簡版區塊,觸發「兩種 sentinel 並存拒絕處理」的新防呆,或在 uninstall 端被誤判成單純的舊格式區塊而挖掉)。已修正:全部補上 `cwd=str(root)`(獨立臨時目錄),並在提交前用 `git status --porcelain CLAUDE.md`/`git diff CLAUDE.md` 確認本 repo 自己的 `CLAUDE.md` 未被測試副作用汙染、與 commit 前 `git checkout -- CLAUDE.md` 一致。

## 相關模組

- [[Systems/slim-install-安裝器]]
- [[Systems/slim-uninstall-一行卸載]]
- [[Systems/slim-gen-生成器]]
- [[Systems/slim-readme]]
- [[Projects/公開精簡版_計劃]]
