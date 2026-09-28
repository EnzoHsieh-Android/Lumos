severity: major
席名: 外家否決3-codex

## F1 合法的引號 job 名會被誤當成 steps，後續 job 可覆寫掉淺層 clone 警告

severity: major
blocking: 是 — CI 的兩道筆記閘會在 shallow clone 回 rc0 跳過，而 doctor 同時漏報，`--no-verify` 後沒有後盾

引句:「m = re.match(r"^(\s+)([\w.-]+):\s*$", ln)」

file: `scripts/lumos:24992`
file: `scripts/lumos:25034`
file: `docs/lumos-toolchain-knowledge/Projects/筆記內容審_計劃.md:130`

GitHub Actions 允許 job ID 寫成 `"audit"`。正規表示式不接受引號，解析器遂把巢狀的 `steps:` 當 job 名；下一個同樣使用引號的 job 又覆寫 `jobs["steps"]`。若第一個 job 呼叫 `note-audit check` 卻沒設 `fetch-depth: 0`，helper 最後回空集合。全檔字串掃描又看得到呼叫，所以「CI 沒呼叫」也不會報。實際 CI 在 shallow clone 裡會把檢查當環境跳過並回 0。

最小重現：

```sh
python3 -c 'import runpy; m=runpy.run_path("scripts/lumos",run_name="audit"); y="jobs:\n  \"audit\":\n    steps:\n      - uses: actions/checkout@v4\n      - run: python3 scripts/lumos note-audit check --diff x\n  \"later\":\n    steps:\n      - run: echo ok\n"; P=type("P",(),{"name":"ci.yml","read_text":lambda self,**_:y}); print(m["_ci_jobs_calling_without_full_history"]([P()],"note-audit check"))'
```

輸出：

```text
[]
```

此處應至少回 `[('ci.yml', 'audit')]`。同一個 helper 也供 `note-shape` 使用，因此第一、第二層會一起漏報。

## F2 只暫存舊路徑刪除時，decision-amend 會放過已推送決策

severity: major
blocking: 是 — 已存在遠端的決策可被誤判為未推送，破壞 S12 要求的「已推只能翻案」

引句:「gone = _lens_git(root, "ls-files", "--deleted", "--", vrel)」

file: `scripts/lumos:24900`
file: `scripts/lumos:24917`
file: `docs/lumos-toolchain-knowledge/Projects/筆記內容審_計劃.md:126`

遠端已有 `Old.md#d1` 時，若使用者把它搬成 `New.md`，但只用 `git add -u Old.md` 暫存舊路徑刪除，新路徑仍是 untracked：

- `ls-files --error-unmatch New.md` 找不到。
- 舊路徑已從 index 移除，因此 `ls-files --deleted` 也是空的，新增的拒絕條件不成立。
- `git diff <remote>` 不包含 untracked 的 `New.md`，只得到刪除，沒有 rename map。
- 程式轉而查遠端的 `New.md`，當然找不到，遂允許修改遠端早已有的 `d1`。

最小重現狀態：

```sh
mv docs/x-knowledge/Systems/Old.md docs/x-knowledge/Systems/New.md
git add -u -- docs/x-knowledge/Systems/Old.md
git status --short
lumos decision-amend Systems/New d1 --field context --text changed
```

輸出會是：

```text
D  docs/x-knowledge/Systems/Old.md
?? docs/x-knowledge/Systems/New.md
✓ decision-amend Systems/New d1.context 改好了(這條決策還沒推上去)
```

我用相同 Git 回傳形狀直接驅動函式，實際結果也是：

```text
✓ decision-amend Systems/New.md d1.context 改好了(這條決策還沒推上去)
rc= 0
```

## F3 終點找不到改成 rc2 後，pre-push 仍把它當成放行

severity: major
blocking: 是 — 這次修正沒有讓本機推送閘 fail-closed；只有 CI 事後變紅

引句:「print(f"擋下:範圍 {diff_range} 的終點在本機找不到——範圍寫錯了?", file=sys.stderr)」

file: `scripts/hooks/pre-push:218`
file: `scripts/hooks/pre-push:236`
file: `scripts/hooks/pre-push:247`
file: `.github/workflows/ci.yml:134`

`home check` 與 `note-shape` 現在對缺失終點回 rc2，但 pre-push 兩處都明確只在 rc1 時 `exit 1`，其餘非零繼續。於是清單所稱「終點找不到不放行」只對直接呼叫與 CI 成立，本機掛鉤仍 fail-open；CI wrapper 則會傳遞 rc2，造成提交已到遠端後才紅燈。

最小重現：

```sh
set +e
python3 scripts/lumos home check --diff HEAD..definitely-missing-tip --repo . >/dev/null 2>&1
direct=$?

hook_rc=0
python3 scripts/lumos home check --diff HEAD..definitely-missing-tip --repo . >/dev/null 2>&1 || hook_rc=$?
if [[ "$hook_rc" -eq 1 ]]; then final=1; else final=0; fi

echo "direct_rc=$direct captured=$hook_rc prepush_decision=$final"
```

輸出：

```text
direct_rc=2 captured=2 prepush_decision=0
```

`prepush_decision=0` 表示掛鉤繼續推送。相同 rc 經 CI 現有 wrapper 則以 exit 2 結束。

## F4 共用全零常數只接受 40 碼，倒退破壞原有的 64 碼刪分支判定

severity: major
blocking: 是 — SHA-256 repository 的合法刪分支範圍會被三道指令當成參數錯誤，CI 可因此無故紅燈

引句:「if _ZERO_SHA_RE.fullmatch(b):」

file: `scripts/lumos:29112`
file: `scripts/lumos:29142`
file: `scripts/lumos:23391`

修正前 `note-audit` 明確接受 `0{40}|0{64}`；現在三道檢查都改用 `_ZERO_SHA_RE`，但該常數仍只有 `0{40}`。同檔的 `_LENS_SHA_RE` 已接受 40 或 64 碼，這次共用化因此是實際倒退，不是刻意取消 SHA-256 支援。

最小重現：

```sh
z64=0000000000000000000000000000000000000000000000000000000000000000

python3 scripts/lumos home check --diff "HEAD..$z64" --repo .; echo home_rc=$?
python3 scripts/lumos note-shape --diff "HEAD..$z64" --repo .; echo shape_rc=$?
python3 scripts/lumos note-audit check --diff "HEAD..$z64" --repo .; echo audit_rc=$?
```

輸出：

```text
擋下:範圍 HEAD..0000000000000000000000000000000000000000000000000000000000000000 的終點在本機找不到——範圍寫錯了?
home_rc=2
擋下:範圍 HEAD..0000000000000000000000000000000000000000000000000000000000000000 的終點在本機找不到——範圍寫錯了?
shape_rc=2
擋下:範圍 HEAD..0000000000000000000000000000000000000000000000000000000000000000 的終點在本機找不到——範圍寫錯了?
audit_rc=2
```

合法刪分支應三者皆跳過並回 rc0。

總結: 最嚴重 severity: major；blocking 4 條。