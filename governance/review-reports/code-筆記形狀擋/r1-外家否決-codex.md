severity: major

## F1 非 ASCII 筆記路徑被 Git 引號化後整篇漏掃
severity: major
blocking: 是 —— 常見的中文筆記名稱會同時繞過 S1 行號引用與 S3 來源檢查。

引句:「path = nfc(p[2:]) if p.startswith("b/") else None」

`_ns_diff` 沒關閉 `core.quotePath`，Git 會把中文路徑輸出成以雙引號開頭的 C-style 路徑；`_ns_parse_added` 因此把 `path` 設成 `None`。`--staged` 完全沒有候選行；`--diff` 雖從 `--name-only -z` 得到最終路徑，但 `texts` 沒收到該提交的新增行，仍全部跳過。

file: `scripts/lumos:23510`  
file: `scripts/lumos:23512`  
file: `scripts/lumos:23551`  
file: `scripts/lumos:23668`

最小重現：

```sh
python3 -c 'import pathlib,runpy; m=runpy.run_path("scripts/lumos"); raw=m["_ns_diff"](pathlib.Path(".").resolve(),"HEAD^","HEAD","--","docs/lumos-toolchain-knowledge"); h=[x for x in raw.decode("utf-8","surrogateescape").splitlines() if x.startswith("+++ ")]; print(h[0]); print("parsed paths:",sorted(m["_ns_parse_added"](raw)))'
```

輸出：

```text
+++ "b/docs/lumos-toolchain-knowledge/Systems/\346\257\217\346\224\257\346\252\224\346\234\211\345\256\266.md"
parsed paths: []
```

## F2 保留遠端 feature branch 時，PR merge 可完全繞過 CI 後盾
severity: major
blocking: 是 —— `--no-verify` 推上的違規在 PR 與 main merge 兩次 CI 都不會受檢。

引句:「if: github.event_name == 'push'」

PR workflow 直接跳過 note-shape。合併後的 main push 會抓回所有 feature refs，只刪 `origin/$BRANCH`；接著 `_ns_range_added` 用 `--not --remotes` 排除仍由 feature ref 可達的全部投稿提交。剩下的一般 merge commit只檢查「兩個 parent 都沒有」的行，而違規行已存在於第二個 parent，故再次被排除。

file: `.github/workflows/ci.yml:124`  
file: `.github/workflows/ci.yml:130`  
file: `scripts/lumos:23535`  
file: `scripts/lumos:23566`

以 repo 既有 merge/遠端 branch 重現相同 reachability：

```sh
M=3af0820c2665880a2ffdaddd3aa0a36a232a8f2f
P1=3adb76988b56c4d2826d2322155811d148282a45
R=refs/remotes/origin/feat/public-slim-handoff
[ pull_request = push ] || echo PR_GATE=SKIP
echo ALL=$(git rev-list "$P1..$M" | wc -l | tr -d ' ') AFTER_NOT_REMOTE=$(git rev-list "$P1..$M" --not "$R" | wc -l | tr -d ' ')
git rev-list --oneline "$P1..$M" --not "$R"
```

輸出：

```text
PR_GATE=SKIP
ALL=28 AFTER_NOT_REMOTE=1
3af0820c merge: 公開精簡版離職交接工具鏈(feat/public-slim-handoff)
```

## F3 同行合法 pin 會吃掉同一路徑的未釘版本引用
severity: major
blocking: 是 —— 一行同時放合法 pinned ref 與普通 ref，即可繞過 S1。

引句:「if not l or (p, l) in pinned:」

抽取器用 `(path, line)` 對 `full` 去重，不區分 pin；之後 `_ns_check_line` 又以相同二元組跳過所有 `pinned` 項。於是先出現的合法 pin 會讓同行的 `scripts/lumos:1` 消失。

file: `scripts/lumos:19917`  
file: `scripts/lumos:19919`  
file: `scripts/lumos:23600`  
file: `scripts/lumos:23611`

最小重現：

```sh
python3 -c 'import pathlib,runpy,subprocess; m=runpy.run_path("scripts/lumos"); root=pathlib.Path(".").resolve(); sha=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()[:12]; tip=m["_lens_full_sha"](root,"HEAD"); files=m["_nodehome_list"](root,tip)[0]; rd=m["_nodehome_reader"](root,tip); f=lambda s:m["_ns_check_line"](root,s,"body",files,rd,{"scripts"},{"lumos":["scripts/lumos"]}); print("unpinned-only =",f("見 `scripts/lumos:1`")); print("valid-pin + unpinned =",f(f"見 `scripts/lumos@{sha}:1` 以及 `scripts/lumos:1`"))'
```

輸出：

```text
unpinned-only = [('程式行號引用', '`scripts/lumos:1`', ...)]
valid-pin + unpinned = []
```

## F4 UTF-8 BOM 會把 summary 誤判成 body
severity: major
blocking: 是 —— 合法 UTF-8 BOM 筆記可繞過所有 FACT/FLOW/DEP 來源檢查。

引句:「if not lines or lines[0].strip() != "---":」

筆記以 `decode("utf-8")` 解碼，BOM 被保留；第一行變成 `\ufeff---`，因此 `_ns_regions` 將整篇標成 `body`。來源規則只在 `region == "summary"` 執行。既有 vault loader 明確使用 `utf-8-sig` 支援 BOM，故不能假設這類檔案非法。

file: `scripts/lumos:23484`  
file: `scripts/lumos:23621`  
file: `scripts/lumos:23682`  
file: `scripts/lumos:329`

最小重現：

```sh
python3 -c 'import runpy; m=runpy.run_path("scripts/lumos"); text="\ufeff---\nsummary: |-\n  FACT:門檻 180 秒\n---\n# A\n"; regs=m["_ns_regions"](text); i=text.splitlines().index("  FACT:門檻 180 秒"); print("FACT region:",regs[i]); print("violations:",m["_ns_check_line"](None,"  FACT:門檻 180 秒",regs[i],{},lambda p:None,set(),{}))'
```

輸出：

```text
FACT region: body
violations: []
```

## F5 同名非程式無副檔名檔會讓唯一程式 basename 引用漏檢
severity: major
blocking: 是 —— 違反 S1「程式檔裡恰好一支同名就要擋」的明文條款。

引句:「if _nodehome_code_kind(p) is not None:」

建立 `by_name` 時，所有無副檔名檔都因 `_nodehome_code_kind` 回傳 `shebang?` 而被計入，尚未核對是否真的有 shebang。若 `scripts/tool` 是唯一程式、另有純文字 `fixtures/tool`，`tool:2` 的候選數會錯成二，直接跳過。

file: `scripts/lumos:22446`  
file: `scripts/lumos:23659`  
file: `scripts/lumos:23617`

最小重現：

```sh
python3 -c 'import runpy; m=runpy.run_path("scripts/lumos"); files={"scripts/tool":"100755","fixtures/tool":"100644"}; data={"scripts/tool":b"#!/bin/sh\necho ok\n","fixtures/tool":b"plain text\n"}; rd=lambda p:data.get(p); by={}; [by.setdefault(p.rsplit("/",1)[-1],[]).append(p) for p in files if m["_nodehome_code_kind"](p) is not None]; print("actual code files:",[p for p in files if m["_ns_is_code"](p,rd,files)]); print("by_name:",by); print("violations:",m["_ns_check_line"](None,"見 `tool:2`","body",files,rd,{"scripts","fixtures"},by))'
```

輸出：

```text
actual code files: ['scripts/tool']
by_name: {'tool': ['scripts/tool', 'fixtures/tool']}
violations: []
```

## F6 官方 reference 的 FLOW/DEP 範例仍會被新閘拒絕
severity: minor
blocking: 否 —— runtime 閘仍能運作，但官方入口會教使用者寫出必然被擋的摘要。

引句:「- **Systems**: WHY + RULE + PITFALL 為主；FLOW/DEP 只寫指針；程式碼查得到的現況一律不寫，程式碼答不了的照〈寫筆記時〉帶 `[來源:…]`」

同一張符號表仍把 `FLOW:` 範例寫成 `reserve→complete→void`，`DEP:` 寫成 `[[Billing]][[Inventory]]`，兩者都沒有 `[來源:…]`。照表格複製到 summary 後，`_NOTE_SHAPE_PREFIX_RULES` 會直接擋下。

file: `skills/lumos-project-notes/reference.md:404`  
file: `skills/lumos-project-notes/reference.md:411`  
file: `skills/lumos-project-notes/reference.md:425`

總結: 最高 severity major；blocking 5 條。