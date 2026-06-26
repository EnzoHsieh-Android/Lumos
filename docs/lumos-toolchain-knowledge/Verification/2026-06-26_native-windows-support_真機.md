---
type: verification
status: pass
feature: 原生 Windows 支援(純 python 單一源 + PowerShell 薄入口 + junction/.cmd shim)
commit: 07a46dd
date: 2026-06-26
valid_under:
  - "scripts/lumos 安裝四函式(_install_skills/_scaffold_project/_install_hooks_py/_link_or_copy)+ cmd_install 結構未變"
  - "merge-claude-settings.py 的 _hook_cmd 解析直呼 + _equivalent 按路徑去重未變"
  - "Python ≥ 3.8 stdlib(subprocess/pathlib/shutil/os.name)"
  - "測試以 t_-prefixed 函式自動發現(scripts/test_lumos.py 框架未換)"
  - "macOS(darwin)+ 原生 Windows(PowerShell + Git for Windows 自帶 bash)+ python on PATH"
revalidate_when:
  - "安裝邏輯改動(skills 連結方式、scaffold 夾數/結構、hooksPath/Claude hooks 複製、settings 註冊格式)"
  - "Claude Code 改變 Windows 上 hook command 的呼叫約定或 shell(目前 Git Bash)"
  - "新增 Windows CI(屆時手動清單可降為輔助)"
  - "測試框架改用 pytest 或換 test profile"
  - "納入新平台/新 shell(WSL、純 PowerShell git)"
tags:
  - type/verification
  - status/pass
---
# 驗證:原生 Windows 支援

## 單元測試(macOS,可信綠底 oracle)
- `scripts/test_lumos.py` 真 Windows baseline 起初 **147 過 / 29 敗**——根因是紙審 3 輪+Mac 都重現不了的 pre-existing bug:lumos 自己 `write_text(encoding=utf-8)`(無 `newline=`)在 Windows text mode 寫出 CRLF,而 `load_raw_for_edit` 又拒絕 CRLF(自寫又自拒)。→ Task 0「行尾/編碼地基」(`_write_lf` 強制 LF + runner UTF-8 stdout + `.gitattributes`)先建可信綠底。
- Task 0-6 實作完:**單元測 200 全綠**,涵蓋 `t_scaffold_project`(6 夾含 Sessions + MOC/index.md + .gitignore + CLAUDE.md 區塊、idempotent)、`t_install_hooks_py`(hooksPath + Claude hooks 複製 + settings 去重不雙註冊)、`t_install_includes_skills`(install 連帶裝 skills)、`t_install_skills_unix`、`t_hooks_python_fallback`。

## design-loop(紙審,3 輪皆有真缺陷,從未乾淨輪)
- r1(sonnet,major):canary 抓到,**4 個 major 辯方查證全坐實**(install-hooks 漏複製 Claude hooks、junction 可跨碟、Claude hook shebang Windows 不認需 resolved-python、PATH 寫死 `:`)。
- r2(sonnet,blocker):又揪 **2 個真 blocker**(cmd_install 漏接 skills→Windows skills 全空;merge-settings command 寫死裸路徑無 resolved-python 實作路徑)+ 夾數 5→6。
- r3(sonnet,major):mklink /J 對個別檔必失敗(.py 該 copy)、command 格式變後去重失效會雙註冊、測試/手動清單 stale「5 夾」。
- 觀察:findings 逐輪變局部細節,架構穩定,但**仍未有乾淨輪**——印證最大誠實天花板「無 Windows CI、紙審難收斂」。

## 真機驗收(真 Windows,Task 7 七步手動閘 → 全閉合)
紙審 3 輪沒抓到、Mac 摸不到的 OS 邊界缺陷,真機連續操作逐一暴露,折成 Task 8 修+重驗:
- **W2(major)**:`_link_or_copy` mklink subprocess `text=True` 預設 UTF-8 解碼,繁中 Windows mklink 輸出走 cp950→`UnicodeDecodeError`。修:`encoding=utf-8, errors=replace`。
- **W4(major,W2 修後揭露)**:junction 不被 `Path.is_symlink()` 認出→舊碼 `rmtree(dst)` 會跟進 junction 刪掉來源 target、且重跑時 junction 殘留→`lumos install` 重跑就壞。修:junction/空夾用 `os.rmdir`(只移連結本身)、真實非空夾才 rmtree。真機連跑兩次 install 已驗冪等 + 來源完好。
- **W3(major)**:`merge-claude-settings.py` hook 路徑前綴 `${HOME}` 只 POSIX 展開,native Windows 不展開→路徑變字面 `${HOME}`→L1/L3 靜默不觸發。修:Windows 用絕對 home。
- **W6(major,重啟後 marker 探針揭露)**:Claude Code 在 Windows **用 Git Bash 跑 hook command**;W3 只正斜線化 home,`_PY`(shutil.which 回 `C:\…\python.EXE`)仍反斜線→Git Bash 吃成 `C:Users`→hook 靜默失敗。(先前在 PowerShell 手動驗 W3「成功」是假象——Claude Code 不用 PowerShell 跑 hook。)修:`_hook_cmd` win32 把 `_PY` 也正斜線化 + 引號。真機 settings 重生為 `"C:/…/python.EXE" "C:/…/x.py"`。
- **W5(假議題,已否證)**:「remote-control 不觸發 hooks」是把 remote-control + W6 反斜線兩變數混在一起的誤判;單變數隔離後 remote-control 模式 marker 照樣出現→真因從頭到尾只有 W6。
- **七步閘結果**:scaffold/hooksPath/settings 遷移/pre-commit 擋 全過;**marker 探針坐實 `PostToolUse`(L3)與 `Stop`(L1)在 native Windows 本地 + remote-control 模式都觸發**(W6 修後)。Task 7 七步全閉合,Windows 全功能到位 → status `windows-verified`(commit `ae439b8`)。

## 方法論教訓(最值錢的部分)
- **驗證正確性 > AI 審計**:3 輪 AI 紙審把設計審硬,但真機跑測試一次就抓到 AI 永遠驗不到的 CRLF 根本問題;W2/W4/W6 是「junction + Windows 碼頁 + Git Bash 路徑語義」的真機物理,只有真機連續操作(裝→重裝→看 hook 真跑)才暴露。
- **連驗證工具本身都要驗**(marker 探針一度因 `from __future__` 順序壞掉誤判)、**在錯的 shell 手動跑會給假綠**(PowerShell 驗 W3 假綠掩蓋 W6)、**歸因前先隔離變數**(W6+切本地混改生出 W5 假議題)。三條同指:真機、照真實執行路徑、單變數驗證,勝過任何推測。
