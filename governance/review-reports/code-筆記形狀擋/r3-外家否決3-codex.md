severity: blocker

## F1 合併時只搬第一上一版的路徑，另一分支新增的違規行會漏檢
severity: blocker
blocking: 是 —— 會放過應被 note-shape 擋下的程式行號引用

當主線已把 `N.md` 攏名成 `M.md`，側分支仍在 `N.md` 新增 `src/a.py:2`，再合併成 `M.md` 時：

- 側分支新增文字記在 `by_path[N.md]`。
- `_carry` 只套第一上一版到合併結果的改名，因此不會搬到 `M.md`。file: `scripts/lumos:23597`
- 第二上一版的 `N.md → M.md` 對照只用來讀 blob。file: `scripts/lumos:23612`
- 合併行因已存在於側分支而不算 merge-new；最終候選只有 `M.md`，其文字集合為空，於是被跳過。file: `scripts/lumos:23771`

引句:「pren = [_renames(pp, sha) or {} for pp in parents]」

最小重現：

```sh
python3 - <<'PY'
import runpy
m = runpy.run_path("scripts/lumos")
g = m["_ns_range_added"].__globals__
old = "docs/kg-knowledge/Systems/N.md"
new = "docs/kg-knowledge/Systems/M.md"
bad = "見 `src/a.py:2`"

g["_nodehome_git"] = lambda root, *a: b"side base\nmerge main side\n"
g["_ns_diff"] = lambda root, *a: (
    f"+++ b/{old}\t\n@@ -1,0 +2 @@\n+{bad}\n".encode()
    if a[0:2] == ("base", "side") else b""
)

def fake_git(root, *a):
    pair = a[4:6] if len(a) > 5 and a[0] == "diff" else ()
    if "--name-status" in a:
        if pair == ("side", "merge"):
            return f"R100\0{old}\0{new}\0".encode()
        if pair == ("main", "merge"):
            return f"M\0{new}\0".encode()
        return b""
    if "--name-only" in a or "--diff-filter=AMR" in a:
        return f"{new}\0".encode()
    return b""

g["_ns_git"] = fake_git
g["_nodehome_cat_blobs"] = lambda root, specs: [
    f"clean\n{bad}\n".encode(),
    b"clean\n",
    f"clean\n{bad}\n".encode(),
]
got = m["_ns_range_added"](
    ".", "base", "merge", "docs/kg-knowledge", exclude_remote=False
)
print(got)
assert bad in got[0].get(new, set()), "終點 M.md 漏掉 side 新增行"
PY
```

輸出：

```text
({'docs/kg-knowledge/Systems/N.md': {'見 `src/a.py:2`'},
  'docs/kg-knowledge/Systems/M.md': set()},
 ['docs/kg-knowledge/Systems/M.md'])
AssertionError: 終點 M.md 漏掉 side 新增行
```

## F2 空的 regen 值也會啟用 [src:] 豁免
severity: blocker
blocking: 是 —— 一般筆記可用 `regen: ""` 繞過程式行號引用閘

`parse_frontmatter` 把 `regen: ""` 解析成空字串，Check J 也不把它當重建筆記；但 note-shape 用原始文字正則判斷，只要冒號後有非空白字元便設成 `regen=True`。接著 summary 裡的 `[src:src/a.py:5]` 被整段刪掉，零違規通過。file: `scripts/lumos:23767`、`scripts/lumos:23658`

引句:「regen = bool(_fm) and any(re.match(r"^regen:\s*\S", x) for x in _fm)」

最小重現：

```sh
python3 -c 'import runpy,re; from pathlib import Path
m=runpy.run_path("scripts/lumos")
text="---\nregen: \"\"\nsummary: |-\n  KEY:證據 [src:src/a.py:5]\n---\n"
fm,_=m["split_frontmatter"](text)
fields,_,_=m["parse_frontmatter"](fm)
regen=any(re.match(r"^regen:\s*\S",x) for x in fm)
out=m["_ns_check_line"](Path("."),"KEY:證據 [src:src/a.py:5]","summary",
 {"src/a.py"},lambda _:b"x\n",{"src"},lambda _:[],regen)
print(repr(fields["regen"]),regen,out)
assert out'
```

輸出：

```text
'' True []
AssertionError
```

## F3 全形逗號沒有進指路行正則，合法 DEP 行會被誤擋
severity: major
blocking: 是 —— 會拒絕上一輪明確要求放行的純連結指路行

正則的分隔符寫成 `|,|,|`，重複兩次半形逗號，沒有 `，`。新增測試雖命名為「全形逗號」，輸入卻是 `DEP:[[A]],[[B]]`，因此沒有覆蓋真正的全形字元。file: `scripts/lumos:23650`、`scripts/test_lumos.py:48537`

引句:「_NS_POINTER_ONLY_RE = re.compile(r"^(?:\s*(?:\[\[[^\]|]+\]\]|見|→|,|,|、|\||｜)\s*)*$")」

最小重現：

```sh
python3 -c 'import runpy; from pathlib import Path
m=runpy.run_path("scripts/lumos")
line="DEP:[[A]]，[[B]]"
out=m["_ns_check_line"](Path("."),line,"summary",set(),lambda _:None,set(),lambda _:[],False)
print(bool(m["_NS_POINTER_ONLY_RE"].fullmatch(line.split(":",1)[1])),out)
assert not out'
```

輸出：

```text
False [('現況描述沒寫來源', 'DEP:[[A]]，[[B]]', ...)]
AssertionError
```

## F4 新程式檔喚醒路徑沒有套用 regen-summary 的 [src:] 豁免
severity: major
blocking: 是 —— 合法的重建證據會在檔案變成程式檔時被誤擋

例如 `scripts/future` 原本是三行純文字，regen summary 合法引用 `[src:scripts/future:3]`；之後只把第一行改成 shebang，使它變成程式檔。一般新增行路徑會先依 `regen && summary` 移除 `[src:]`，但喚醒路徑直接把原行送進抽取器，沒有判 region、regen，也沒有套 `SRC_REF_RE.sub`。它隨後把抽出的引用無條件加入違規。file: `scripts/lumos:23794`、`scripts/lumos:23807`、`scripts/lumos:23814`

引句:「fl, _b = _node_code_ref_tokens(ln, top_dirs, bare_text=True, anchors=True, keep_fences=True,」

最小重現：

```sh
python3 -c 'import runpy
m=runpy.run_path("scripts/lumos")
pins=[]; singles=[]
got=m["_node_code_ref_tokens"](
 "KEY:來源 [src:scripts/future:3]",{"scripts"},
 bare_text=True,anchors=True,keep_fences=True,
 pins=pins,singles=singles,exists=lambda p:p=="scripts/future")
print(got,pins,singles)
assert got[0]==[]'
```

輸出：

```text
([('scripts/future', '3')], set()) [] []
AssertionError
```

## F5 refcheck 無法驗證已從目前版本刪除的合法歷史釘版本
severity: major
blocking: 是 —— 會讓既有 refcheck／審查放行閘拒絕合法且不可變的歷史引用

`exists` 只查目前工作樹。若檔案存在於被釘提交、該提交仍在分支歷史上，但檔案後來已刪除，抽取器不會切開 `@提交`；整串遂落到目前版本的 `_validate_repo_ref`，被判成不存在。這違反 S2「對合法釘版本引用應判對得上」。file: `scripts/lumos:19949`、`docs/lumos-toolchain-knowledge/Projects/筆記形狀擋_計劃.md:65`

引句:「full, _bare = _node_code_ref_tokens(text, top_dirs, pins=pins, exists=lambda p_: (repo_root / p_).exists())」

最小重現：

```sh
python3 -c 'import runpy; from pathlib import Path
m=runpy.run_path("scripts/lumos")
sha="b1c9851dc1aa"
text=f"見 `scripts/hooks/claude/verification-rot-check.py@{sha}:1`"
print("resolved_pin=",m["_pin_commit"](Path("."),sha))
got=m["_refcheck_scan"](text,Path("."))
print(got)
assert got[3]==1'
```

輸出：

```text
resolved_pin= b1c9851dc1aa6ecca39880b42ca03fe022e68207
([{'token': 'scripts/hooks/claude/verification-rot-check.py@b1c9851dc1aa',
   'line': '1', 'status': 'missing', 'excerpt': ''}], 1, 0, 0)
AssertionError
```

總結: blocker；blocking 5 條