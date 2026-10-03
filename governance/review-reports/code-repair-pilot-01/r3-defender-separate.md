## Finding 2 — absolute separate-git-dir 指回來源

refute-verdict: agree

severity: major

blocking: 是

引句:「沙盒的隔離動作會寫進那個 git 目錄所屬的 repo——拔掉真遠端、改掉真 hooksPath,防護會靜默失效。」

file: `scripts/scenario_probe.py:483`

file: `scripts/scenario_probe.py:487`

file: `scripts/scenario_probe.py:507`

file: `scripts/scenario_probe.py:510`

file: `scripts/scenario_probe.py:518`

evidence: 487–488 行只驗來源 gitdir 位於來源目錄內，因此來源內的 absolute separate-git-dir 會通過。`rsync -a` 後沒有重新解析副本 gitdir，隨即執行 `remote remove`、設定 `core.hooksPath` 與建立快照。

最小重現:

```sh
git -C "$src" init -q --separate-git-dir "$src/.hidden-git" .
git -C "$src" remote add sentinel "$scratch/sentinel.git"
python3 -c '...; mod.make_sandbox(sys.argv[1])' "$src"
```

`/tmp/r3-separate-gitdir-repro.json` 在 `1c91755a` 與 `4a60b231` 均證實：

```text
source_gitdir_inside_source=true
sandbox_gitdir_equals_source=true
remotes: sentinel → 空
hooks: /dev/null → /tmp/lumos-probe-.../hooks
head: 建立沙盒前後不同
network_executed=false
```

判準沒有過度擴張：這不只是假設風險，沙盒建立已直接刪除來源 remote、改寫來源 hooksPath，並推進來源 HEAD，違反 `make_sandbox` 不污染來源的核心邊界。屬可重現的來源資料與設定損壞，major 不能降級；未執行外部 push 或網路寫入，沒有足夠證據升為 blocker。

concern: 兩個版本都重現，因此來源分類是既有 `make_sandbox` 漏洞；本輪讓 source-probe 更頻繁走到該路徑，但沒有修前正常、修後才壞的證據。

總結最嚴重 severity: major；blocking: 1 條。
