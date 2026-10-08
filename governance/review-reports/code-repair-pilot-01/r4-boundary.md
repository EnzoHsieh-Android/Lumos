severity: blocker

ID: R4-B1
severity: blocker
blocking: true
引句:「for name in r.stdout.split():」
file: `scripts/scenario_probe.py:542`
finding: 沙盒只移除頂層 repo 的 remote、只在頂層 local config 安裝防推 hook；已簽出的 submodule／巢狀 repo 保留原 remote，普通 `git push` 可直接寫到外部。
最小重現: 在臨時頂層 repo 加入指向臨時 bare repo 的 `vendor` submodule，呼叫目前 `make_sandbox(src)`；實測頂層 remote 為空，但 `vendor` 的 remote 為 `origin`、沒有 `core.hooksPath`。於副本 submodule 建空提交後執行 `git -C "$work/vendor" push origin HEAD:refs/heads/escaped` 得 `rc=0`，外側 bare 的 `refs/heads/escaped` 存在。
翻紅判準: 外側 bare 不得出現新 ref；目前 `outside_ref=true`。
分類: 舊漏報；r4-delta 保留原本僅對 `cwd=work` 操作 remote/hook 的做法，新路徑檢查未涵蓋巢狀 Git。

ID: R4-B2
severity: blocker
blocking: true
引句:「subprocess.run(["git", "remote", "remove", name], cwd=str(work), env=genv)」
file: `scripts/scenario_probe.py:544`
finding: `.git/config` 若以 `include.path` 引入外部設定檔中的 remote，`git remote remove` 會失敗；程式未檢查退出碼，也未在移除後確認 remote 清空，沙盒帶著可用外部 remote 繼續啟動模型。
最小重現: 用 `git config --file external.config remote.escape.url <臨時bare>` 建外部設定，再以 `git -C src config include.path <external.config>` 引入。呼叫 `make_sandbox(src)` 時印出 `Could not remove config section 'remote.escape'`，但仍回傳沙盒；`git -C "$work" remote` 輸出 `escape`。執行 `git -C "$work" push --no-verify escape HEAD:refs/heads/escaped` 得 `rc=0`，外側 bare 出現該 ref。
翻紅判準: 任一 remote 移除失敗或移除後仍列得到 remote，都應在模型啟動前 fail closed；目前 `sandbox_remote="escape"` 且 `outside_ref=true`。
分類: 舊漏報；r4 修的是 command/global/system 環境設定注入，既有 local include 與未檢查的 remove 仍存活。

ID: R4-B3
severity: major
blocking: true
引句:「subprocess.run(["git", "clean", "-qfdx"], cwd=str(work), env=_git_env())」
file: `scripts/scenario_probe.py:946`
finding: 共用沙盒逐題還原的 `git checkout` 與 `git clean` 都忽略退出碼；上一題若破壞 Git metadata 或令清理失敗，下一題仍在污染現場執行，最後甚至可回傳成功。
最小重現: 兩題的 mocked runner 共用真臨時沙盒；第一題建立 `poison.txt` 並刪除該臨時副本的 `.git`。兩道清理命令各回 `fatal: not a git repository`，第二題仍被呼叫且看到 `poison=True, git=False`；兩題回傳 passed 時 `main_rc=0`。
翻紅判準: 任一道逐題還原失敗後不得執行下一題，整批應標儀器例外/inconclusive 並回非零碼。
分類: 舊漏報；r4 只替兩個命令補 `_git_env()`，未補退出碼判定或致命停止。

ID: R4-B4
severity: major
blocking: true
引句:「if not isinstance(ident, str) or ident in eligible:」
file: `scripts/scenario_probe.py:147`
finding: Claude adapter 接受空字串工具 ID；`tool_use.id=""` 與 `tool_result.tool_use_id=""` 可互相配對，畸形串流因含標記而直接判 `present`，進一步讓題目通過。
最小重現: 傳入三個 JSON 事件：空 ID 的 Bash `tool_use`、空 ID 且內容含 token 的成功 `tool_result`、`result/subtype=success`。實測 `source_evidence(..., "claude", token) == "present"`，接著 `grade(..., source_state="present") == (True, "ok", True)`。
翻紅判準: 空或非字串 correlation ID 應回 `unknown` 並排除分母；目前輸出 `state=present, grade_passed=true`。
分類: 舊漏報／本輪修復不完整；r4-delta 只補 Codex started/updated 的缺壞 ID，未覆蓋 Claude adapter。

固定席八節點逐條核對：

1. `Systems/codex-harness`：有 finding。B1、B2 破壞「副本推不出去」及 Git 隔離事故邊界；B3 破壞儀器故障不污染後題；B4 讓畸形事件進有效通過。節點自己已警告現有綠測試不可擴張成所有 Git 形狀安全，與本次重現一致。

2. `Systems/測試假綠形態`：已讀，無獨立新增 finding。r4 的已覆蓋案例有修前紅／修後綠及現場檢查；但 50 綠未覆蓋巢狀 Git、local include、共用沙盒清理失敗及 Claude 空 ID，不能拿來反駁 B1–B4。這是覆蓋缺口，未另拆第五條。

3. `Systems/lumos-cli-read`：已讀，無 finding。改動未觸及 search 對 superseded/stale 的三路一致、hidden 計數或輸出通道。

4. `Systems/lumos-cli-lifecycle`：已讀，無 finding。改動未觸及 re-inject sentinel 外內容 byte-equal 保留契約。

5. `Systems/bound-tests-gate`：已讀，無 finding。改動未觸及 impact 固定席綁定測試的真跑、懸空／偽證據／unfilterable 判定或 rc 契約；本次 `r4-test-layers.txt` 為空，無額外機器測試層建議。

6. `Systems/canary-audit`：已讀，無 finding。改動未觸及 record/second 寫後讀回或 second 純 telemetry 契約。

7. `Systems/design-loop`：已讀，無 finding。改動未觸及設計審材必須為 `.md`、條款綁定、句式或回退節判定。

8. `Systems/guard-kill`：已讀，無 finding。改動未觸及 survived/drifted/error rc 優先序或 `--json` stdout 純度契約。

以下腳本可由父代理對同一 baseline/current 各跑一次。參數是該版本的 `scripts/scenario_probe.py`；所有 repo 與 bare 都建立於 `TemporaryDirectory`，每道 Git 命令均使用 `git -C`。

```python
#!/usr/bin/env python3
import contextlib
import importlib.util
import io
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

probe_path = Path(sys.argv[1]).resolve()
spec = importlib.util.spec_from_file_location("scenario_probe_under_test", probe_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def git(cwd, *args, check=False):
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        capture_output=True,
        text=True,
        check=check,
    )


def commit_empty(repo, message="init"):
    git(
        repo, "-c", "user.name=test", "-c", "user.email=t@t",
        "commit", "--allow-empty", "-qm", message, check=True,
    )


def result(sc_id):
    return {
        "id": sc_id,
        "cat": None,
        "passed": True,
        "reason": "ok",
        "first_tool": None,
        "n_calls": 0,
        "calls": [],
        "secs": 0,
        "stderr": "",
        "arm": "with",
        "ever_lumos": False,
        "first_lumos_idx": None,
        "limit_hit": False,
        "result_subtype": "success",
        "truncated": False,
    }


def nested_repo_case(root):
    remote = root / "subremote.git"
    seed = root / "seed"
    src = root / "src-submodule"

    git(root, "init", "-q", "--bare", str(remote), check=True)
    git(root, "clone", "-q", str(remote), str(seed), check=True)
    git(seed, "config", "user.name", "test", check=True)
    git(seed, "config", "user.email", "t@t", check=True)
    (seed / "tracked.txt").write_text("base\n", encoding="utf-8")
    git(seed, "add", "tracked.txt", check=True)
    git(seed, "commit", "-qm", "seed", check=True)
    git(seed, "push", "-q", "origin", "HEAD:refs/heads/main", check=True)

    git(root, "init", "-q", str(src), check=True)
    git(src, "config", "user.name", "test", check=True)
    git(src, "config", "user.email", "t@t", check=True)
    git(
        src, "-c", "protocol.file.allow=always",
        "submodule", "add", "-q", "-b", "main",
        str(remote), "vendor", check=True,
    )
    git(src, "commit", "-qm", "top", check=True)

    work = mod.make_sandbox(src)
    try:
        top_remote = git(work, "remote").stdout.strip()
        nested_remote = git(work / "vendor", "remote").stdout.strip()
        nested_hook = git(
            work / "vendor", "config", "--get", "core.hooksPath"
        )
        commit_empty(work / "vendor", "escape")
        push = git(
            work / "vendor", "push", "-q", "origin",
            "HEAD:refs/heads/escaped",
        )
        outside = git(
            remote, "show-ref", "--verify", "refs/heads/escaped"
        )
        return {
            "top_remote": top_remote,
            "nested_remote": nested_remote,
            "nested_hook_rc": nested_hook.returncode,
            "push_rc": push.returncode,
            "outside_ref": outside.returncode == 0,
        }
    finally:
        shutil.rmtree(work.parent)


def included_config_case(root):
    remote = root / "include-remote.git"
    src = root / "src-include"
    external = root / "external.config"

    git(root, "init", "-q", "--bare", str(remote), check=True)
    git(root, "init", "-q", str(src), check=True)
    commit_empty(src)
    git(
        root, "config", "--file", str(external),
        "remote.escape.url", str(remote), check=True,
    )
    git(
        root, "config", "--file", str(external),
        "remote.escape.fetch",
        "+refs/heads/*:refs/remotes/escape/*", check=True,
    )
    git(src, "config", "include.path", str(external), check=True)

    work = mod.make_sandbox(src)
    try:
        remotes = git(work, "remote").stdout.strip()
        push = git(
            work, "push", "--no-verify", "-q", "escape",
            "HEAD:refs/heads/escaped",
        )
        outside = git(
            remote, "show-ref", "--verify", "refs/heads/escaped"
        )
        return {
            "sandbox_remote": remotes,
            "push_rc": push.returncode,
            "outside_ref": outside.returncode == 0,
        }
    finally:
        shutil.rmtree(work.parent)


def cleanup_case(root):
    src = root / "src-cleanup"
    questions = root / "questions.jsonl"
    git(root, "init", "-q", str(src), check=True)
    commit_empty(src)
    questions.write_text(
        "\n".join(
            json.dumps({"id": x, "prompt": "p", "expect": ["x"]})
            for x in ("q1", "q2")
        ) + "\n",
        encoding="utf-8",
    )
    seen = []

    def fake_runner(sc, work, *args, **kwargs):
        if sc["id"] == "q1":
            (work / "poison.txt").write_text("from q1", encoding="utf-8")
            shutil.rmtree(work / ".git")
        else:
            seen.append({
                "poison": (work / "poison.txt").exists(),
                "git": (work / ".git").exists(),
            })
        return result(sc["id"])

    argv = [
        "probe", "--repo", str(src),
        "--scenarios", str(questions),
    ]
    with (
        patch.object(mod.sys, "argv", argv),
        patch.object(mod, "run_one", side_effect=fake_runner),
        patch.object(mod, "check_scenario_targets", return_value=[]),
        patch.object(mod, "global_skills_health", return_value=[]),
        contextlib.redirect_stdout(io.StringIO()),
        contextlib.redirect_stderr(io.StringIO()),
    ):
        rc = mod.main()
    return {"second_scenario_seen": seen, "main_rc": rc}


def empty_id_case():
    token = "LUMOS_READ_" + "a" * 32
    events = [
        {
            "type": "assistant",
            "message": {"content": [{
                "type": "tool_use",
                "id": "",
                "name": "Bash",
                "input": {"command": "cat scripts/lumos"},
            }]},
        },
        {
            "type": "user",
            "message": {"content": [{
                "type": "tool_result",
                "tool_use_id": "",
                "content": token,
                "is_error": False,
            }]},
        },
        {"type": "result", "subtype": "success", "result": "帳本"},
    ]
    state = mod.source_evidence(
        [json.dumps(event) for event in events], "claude", token
    )
    sc = {
        "source_probe": {"path": "scripts/lumos"},
        "answer_expect": ["帳"],
        "expect": ["x"],
    }
    graded = mod.grade(sc, [], "帳本", state)
    return {
        "source_evidence": state,
        "grade_passed": graded[0],
        "grade_reason": graded[1],
    }


with tempfile.TemporaryDirectory(prefix="r4-boundary-pair-") as td:
    root = Path(td)
    output = {
        "nested_repo": nested_repo_case(root),
        "included_config": included_config_case(root),
        "cleanup": cleanup_case(root),
        "empty_id": empty_id_case(),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
```

配對方式：

```sh
pair_root=$(mktemp -d /tmp/r4-pair.XXXXXX)
git -C "$pair_root" clone -q --no-local /Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone "$pair_root/base"
git -C "$pair_root/base" checkout -q 637989b1
python3 /tmp/r4-boundary-repro.py "$pair_root/base/scripts/scenario_probe.py"
python3 /tmp/r4-boundary-repro.py /Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/scripts/scenario_probe.py
```

預期 baseline/current 皆會得到等價的漏洞結果：

```json
{
  "nested_repo": {
    "top_remote": "",
    "nested_remote": "origin",
    "nested_hook_rc": 1,
    "push_rc": 0,
    "outside_ref": true
  },
  "included_config": {
    "sandbox_remote": "escape",
    "push_rc": 0,
    "outside_ref": true
  },
  "cleanup": {
    "second_scenario_seen": [{"poison": true, "git": false}],
    "main_rc": 0
  },
  "empty_id": {
    "source_evidence": "present",
    "grade_passed": true,
    "grade_reason": "ok"
  }
}
```

材料與限制: 完整讀取 `r4-code.patch`、`r4-context.patch`、`r4-delta.patch`；`r4-archive-boundary.patch` 僅核對 Git 隔離、清理與事件證據的歷史段落，未把 archive 當現況，也未讀其他 r4 席報告。HEAD 為 `8922c3c9c11e4234554d94695c31c93973679a99`；`r4-snapshot.patch` SHA256 為 `2e8dae39bcabc1d4793e43e096995d79e84bbcf4edb9c83dea009bdfeb0c2734`。`/tmp/r4-lens.txt` 八個固定席節點已逐條核對；`/tmp/r4-test-layers.txt` 不存在，repo 同名檔為空，故無機器測試層建議。既有 `python3.14 scripts/test_lumos.py -k probe_repair4_` 為 50 passed、0 failed；上述四例均在臨時目錄以本機 bare repo／fixture 重現，未使用網路或真遠端。工作樹狀態與進場時一致，未改檔。

總結: 最嚴重 severity blocker；blocking 4 條。
