severity: major

finding: F1｜S4 只驗 impact 失敗，JSON 解析、base 樹與未預期例外出口沒有紅綠案例；實作若只補命中快取及 impact 分支，四條驗收仍可能全綠，其他出口繼續留鎖。
severity: major
blocking: yes
file: `governance/review-reports/design-背景快取命中清鎖/r1-snapshot.md:20`
file: `governance/review-reports/design-背景快取命中清鎖/r1-snapshot.md:29`
file: `scripts/lumos:34115`
file: `scripts/lumos:34118`
file: `scripts/lumos:34126`
引句:「前掃另查到快取未命中後仍有 impact、JSON、base 樹等錯誤提前出口，也會繞過尾端清理」
最小重現: 已執行以下唯讀檢查，rc 1；S4 缺少 `JSON`、`base 樹`、`未預期例外`：
```sh
python3 - <<'PY'
from pathlib import Path
s = Path("governance/review-reports/design-背景快取命中清鎖/r1-snapshot.md").read_text()
s4 = next(x for x in s.splitlines() if "[S4]" in x)
missing = [x for x in ("JSON", "base 樹", "未預期例外") if x not in s4]
assert not missing, ",".join(missing)
PY
```

finding: F2｜回退依賴「暫停背景暖機入口」才能止損，但設計沒有指定控制點、命令或負責入口；父提交本身仍會由 hook 帶 `--deadline` 進入暖機，單純回到父提交會恢復已知 F1/F2。
severity: major
blocking: yes
file: `governance/review-reports/design-背景快取命中清鎖/r1-snapshot.md:44`
file: `scripts/hooks/claude/dispatch-lens-hook.py:321`
file: `scripts/hooks/claude/dispatch-lens-hook.py:338`
file: `scripts/lumos:34110`
引句:「回退本次分支到父提交 `930915bb` 並暫停背景暖機入口，不恢復等待端按舊狀態刪鎖」
最小重現: 已執行父提交停用控制搜尋，rc 1；找不到暖機 pause/disable 開關：
```sh
git show 930915bb:scripts/lumos |
rg 'LUMOS_.*(DISABLE|PAUSE).*LENS|LENS_.*(DISABLE|PAUSE)|disable.*warm|pause.*warm'
```

finding: F3｜驗證順序未寫 Python 3.14、來源 repo、可解析 main/master 與零 skip 前提。S3 綁定的整合測試缺 `.git`、主線或足夠歷史時會轉 skip；使用 `-k` 跑子集時，runner 不會因 skip 判紅，因此可能把「沒驗到」記成成功。
severity: major
blocking: yes
file: `governance/review-reports/design-背景快取命中清鎖/r1-snapshot.md:48`
file: `scripts/test_lumos.py:16303`
file: `scripts/test_lumos.py:16324`
file: `scripts/test_lumos.py:31621`
file: `scripts/test_lumos.py:31687`
引句:「完成後記獨立驗證紀錄、審查快照與處置；前案仍因 F2 未修保持 pending」
最小重現: 已執行驗證前提檢查，rc 1；驗證節缺 `python3.14`、`來源 repo`、`main`、`零 skip`：
```sh
python3 - <<'PY'
from pathlib import Path
s = Path("governance/review-reports/design-背景快取命中清鎖/r1-snapshot.md").read_text()
v = s.split("## 驗證順序", 1)[1]
missing = [x for x in ("python3.14", "來源 repo", "main", "零 skip") if x not in v]
assert not missing, ",".join(missing)
PY
```

問題與邊界：已讀，除 F1 外無 finding。  
實務隱患：已讀，無 finding。  
發布條件：已讀；「F2 未修、不得聲稱整體放行」已寫清，無額外 finding。

總結：最嚴重 severity: major；blocking: 3
