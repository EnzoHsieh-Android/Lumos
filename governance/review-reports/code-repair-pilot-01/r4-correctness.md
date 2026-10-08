severity: blocker

R4-C1：repo-local include 可同時復活 remote、覆蓋防推 hook

severity: blocker  
blocking: true  
引句:「subprocess.run(["git", "remote", "remove", name], cwd=str(work), env=genv)」  
file: `scripts/scenario_probe.py:544`

問題：`_git_env()` 只隔離 command-scope、global 與 system config，沒有隔離副本 `.git/config` 內的 `[include]`。若 include 的外部設定定義 remote 與 `core.hooksPath`，`git remote remove` 會失敗，但這裡未檢查 return code；後續寫入的 sandbox hook 又被 include 覆蓋。被測模型因此能看到有效 remote，且 push 不會經過「禁止 push」hook。這直接破壞不可逆副作用隔離。

分類：原有漏報／r4 修補不完整。基線已有未檢查的 remote remove；r4 新增的 `GIT_CONFIG*` 清洗只封住環境與全域設定，沒有封住 local include。

最小重現程式，全部只用臨時 repo、本機 bare remote 與 `--dry-run`：

```python
import importlib.util
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("sp", "scripts/scenario_probe.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

with tempfile.TemporaryDirectory(prefix="r4-local-include-") as td:
    root = Path(td)
    src, bare = root / "src", root / "bare.git"
    empty_hooks, conf = root / "empty-hooks", root / "injected.config"

    def git(cwd, *args):
        return subprocess.run(
            ["git", "-C", str(cwd), *args],
            text=True, capture_output=True, check=True,
        )

    git(root, "init", "-q", str(src))
    git(root, "init", "-q", "--bare", str(bare))
    empty_hooks.mkdir()
    git(src, "config", "user.name", "test")
    git(src, "config", "user.email", "test@example.invalid")
    git(src, "commit", "--allow-empty", "-qm", "seed")

    git(src, "config", "--file", str(conf), "remote.escape.url", str(bare))
    git(src, "config", "--file", str(conf), "remote.escape.fetch",
        "+refs/heads/*:refs/remotes/escape/*")
    git(src, "config", "--file", str(conf), "core.hooksPath", str(empty_hooks))
    git(src, "config", "--add", "include.path", str(conf))

    with patch.object(mod.tempfile, "mkdtemp", return_value=str(root / "copy")):
        work = mod.make_sandbox(src)

    env = mod._git_env()
    remotes = subprocess.run(
        ["git", "-C", str(work), "remote"],
        env=env, text=True, capture_output=True,
    ).stdout.strip()
    hooks = subprocess.run(
        ["git", "-C", str(work), "config", "--get", "core.hooksPath"],
        env=env, text=True, capture_output=True,
    ).stdout.strip()
    push = subprocess.run(
        ["git", "-C", str(work), "push", "--dry-run",
         "escape", "HEAD:refs/heads/probe"],
        env=env, text=True, capture_output=True,
    )

    assert remotes == ""
    assert hooks == str(work.parent / "hooks")
    assert push.returncode != 0
```

實際結果：

```text
error: Could not remove config section 'remote.escape'
remote='escape'
hooks='<臨時目錄>/empty-hooks'
push.returncode=0
```

判準：三個 assert 應全綠；現況全數翻紅。現有 `t_probe_repair4_git_config` 只測 `GIT_CONFIG_COUNT`、`GIT_CONFIG_PARAMETERS`、global 與 system 四種環境注入，沒有 repo-local include，故既有 50 項仍全綠。

事件狀態／不完整呼叫：已讀，無 finding。缺失或畸形 Codex started/updated ID 會落為 unknown；完整未讀維持有效失敗；正證據可覆蓋其他不完整呼叫。

有效分母／fatal 清理：已讀，無 finding。另做「先一場有效通過、再 source cleanup fatal」入口重現，得到 rc3、輸出 `inconclusive=true`，且停止後續 runner；先前有效樣本仍按既有規則留在有效分母。自主迴圈仍會因 fatal 前綴造成解析不等而發 LINE。沒有找到要求 fatal 必須撤銷先前有效樣本或同週重跑的合約，因此未將表面 `1/1` 升格為 finding。

新舊資料互讀：已讀，無 finding。新版以 `GRADER_VERSION=2026-10-03-source-results` 分界，舊摘要沒有結果證據時回 unknown，沒有偽造新版正證據或改寫舊歷史。

寫一半與專用副本清理：除 R4-C1 的 Git 設定逃逸外，已讀，無其他 finding。專用副本準備失敗會清理；清理失敗會 fatal 停批；來源檔、AST、symlink、hardlink、越界路徑均有守衛。

固定席合約適用／影響：

- `Systems/codex-harness`：適用，是 `scenario_probe.py` 與測試的家；R4-C1 直接影響其沙盒隔離責任。
- `Systems/測試假綠形態`：適用。現有 r4 測試對已覆蓋案例有現場前置斷言；local include 合法現場未納入，缺口已併入 R4-C1。
- `Systems/lumos-cli-read`：不適用；未改 search 的 superseded/stale 濾網。
- `Systems/lumos-cli-lifecycle`：不適用；未改 re-inject sentinel 外 byte-equal 行為。
- `Systems/bound-tests-gate`：不適用；未改固定席綁定測試的執行與 rc。
- `Systems/canary-audit`：兩條合約均不受影響；未改 record readback 或 second telemetry。
- `Systems/design-loop`：不適用；未改處置閘第五步。
- `Systems/guard-kill`：兩條合約均不受影響；未改 rc 優先序或 JSON 純度。
- lens 中超出上限而只列名的節點沒有附合約正文，本席不從名稱推造額外合約。

已讀材料：

- `python-idioms/SKILL.md`
- `lumos-project-notes/SKILL.md`
- `CLAUDE.md`
- `docs/lumos-toolchain-knowledge/MOC/index.md`
- `/tmp/r4-lens.txt`
- `r4-code.patch`
- `r4-context.patch`
- `r4-delta.patch`
- `r4-archive-correctness.patch`
- `r4-snapshot.patch`，SHA256 已核對為 `2e8dae39bcabc1d4793e43e096995d79e84bbcf4edb9c83dea009bdfeb0c2734`

Archive 核對深度：全量索引其內嵌 diff，逐段核對 source-probe、fatal、分母、Git 隔離與相應歷史測試證據；未把 archive 當現況權威，未重跑舊模型審查。歷史證據與「原有 Git 隔離漏看、後續逐輪補洞」一致，無獨立 archive finding。

驗證：

- `python3.14 scripts/test_lumos.py -k probe_repair4`：50 passed、0 failed。
- `python3.14 scripts/test_lumos.py -k probe_source_probe`：59 passed、0 failed。
- R4-C1 臨時 repo 重現：remote 保留、hook 被覆蓋、dry-run push rc0。
- 未執行真模型、網路推送、全套測試或部署。
- `/tmp/r4-test-layers.txt` 本席讀取時不存在；上游回報生成命令 rc0、stdout 空，按「無機器測試層建議」處理。
- 未讀同輪其他 r4 席報告。

總結：最嚴重 severity=blocker；blocking=1
