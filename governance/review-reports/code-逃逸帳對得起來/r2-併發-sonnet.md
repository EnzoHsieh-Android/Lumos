severity: major

## F1 `escape-stats` 對同一本帳分兩次不同步讀取,同一筆逃逸可能同時被算進「漏網」又算進「已撤回」
severity: major
blocking: yes
引句:「by_loop = _escape_review_rows_by_loop(env)」
file: `scripts/lumos:9893-9914`(函式 `_escape_stats`)

`_escape_stats` 在同一次呼叫裡把 `.escape-log.jsonl` 讀了兩次、`.canary-log.jsonl` 也讀了兩次,而且沒有用任何鎖或單一快照把這幾次讀取釘在同一個時間點:

- 第 9895 行 `rows = _escape_rows_for(env)`——第一次讀 `.escape-log.jsonl`(過濾撤回),後面拿 `rows` 去分桶(counted/leaked)。
- 第 9914 行 `"withdrawn": len(_escape_withdrawn_targets(_escape_raw_rows(env)))`——第二次讀 `.escape-log.jsonl`(原始、不過濾)。
- 第 9896 行 `review_ids = _review_loop_ids(env)` 與第 9897 行 `by_loop = _escape_review_rows_by_loop(env)`——分別讀了一次 `.canary-log.jsonl`,而 r2 這版把 `_review_loop_ids` 改成 `return set(_escape_review_rows_by_loop(env))`(patch 第 65 行),意思是這兩行現在literally 呼叫同一支函式、算同一份東西,卻各自重新掃檔,r2 的整併沒有把呼叫端(`_escape_stats`)的重複 I/O 一併拿掉。

讀者(escape-stats)不上 `_vault_write_lock`(這是設計上刻意的,寫者才上鎖),這本身沒問題;但在同一次統計裡分兩個不同時間點讀同一份帳,等於拿兩個時間點不一致的快照湊出一份結果。當另一個行程在這兩次讀取之間跑完一次 `--withdraw`,「撤回後統計不算它」(計劃第三節)這條保證會在單次 `escape-stats` 輸出裡直接被打破:同一個 token 同時出現在 `leaked`(用撤回前那次讀到的快照算的)與 `totals.withdrawn`(用撤回後那次讀到的快照算的)兩邊。

重現(在乾淨 repo 副本上跑,不動到真 vault):

```
cd /private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/ba2fc358-b2c4-4fe8-b8cf-9883c1468562/scratchpad/escimpl/exp2-併發/repo
python3 - <<'EOF'
import importlib.machinery, importlib.util
loader = importlib.machinery.SourceFileLoader("m", "scripts/lumos")
spec = importlib.util.spec_from_loader("m", loader)
m = importlib.util.module_from_spec(spec)
loader.exec_module(m)

import tempfile, json
from pathlib import Path

d = Path(tempfile.mkdtemp())
vault = d / "vault"; vault.mkdir(); (vault / "Projects").mkdir()
canary = d / ".canary-log.jsonl"; gov = d / ".governance-log.jsonl"; esc = d / ".escape-log.jsonl"
canary.write_text(json.dumps({"kind":"none","loop":"甲","round":"r1","tier":"standard","token":"X1"})+"\n", encoding="utf-8")
gov.write_text(json.dumps({"kind":"converged","gate":"design-loop","nodes":["甲"]})+"\n", encoding="utf-8")
before = json.dumps({"token":"E1","loop":"甲","stage":"CI","severity":"major","desc":"d","sha":"a"})+"\n"
after = before + json.dumps({"kind":"withdraw","target":"E1","reason":"誤判了","by":"t","token":"W1"})+"\n"
esc.write_text(before, encoding="utf-8")

# 模擬:_escape_stats 第一次讀 .escape-log.jsonl(算 rows/leaked)時撤回還沒發生,
# 第二次讀(算 withdrawn 總數)時,另一個行程已經把撤回寫進去了——同一次呼叫混用兩個時間點的帳。
orig = Path.read_text
n = {"i": 0}
def racing(self, *a, **kw):
    if str(self) == str(esc):
        n["i"] += 1
        return before if n["i"] == 1 else after
    return orig(self, *a, **kw)
Path.read_text = racing

env = type("E", (), {"vault": vault, "notes": {}})()
st = m._escape_stats(env)
leaked = sum(len(c["leaked"]) for c in st["categories"])
print("leaked total:", leaked, "  withdrawn total:", st["totals"]["withdrawn"])
EOF
```

實跑輸出:`leaked total: 1   withdrawn total: 1`——同一個 E1 一次呼叫裡兩邊都算到了,不是「撤回後統計不算它」而是「撤回前後各留一份痕跡在不同欄位」。這不是刻意構造出不存在的情境:兩次 `Path.read_text` 呼叫確實是 `_escape_stats` 自己發出的(用一支不作弊的計數器驗過,見 F2 的重現指令,兩次都命中同一個檔案路徑),只是把「另一個行程剛好在這兩次讀取中間完成一次撤回」這個真實會發生的時序,用固定回傳值模擬出來,不影響 `_escape_stats` 內部邏輯本身。

## F2 `.canary-log.jsonl` 在單一一次 `lumos loop escape` 呼叫裡被獨立重掃 2 次,r2 把 `_review_loop_ids` 改成呼叫 `_escape_review_rows_by_loop` 卻沒有消掉呼叫端的重複讀
severity: minor
blocking: no
引句:「return set(_escape_review_rows_by_loop(env))」

r2 這版把 `_review_loop_ids(env)` 從原本自己內嵌一段讀檔迴圈,改成 `return set(_escape_review_rows_by_loop(env))`(patch 第 65 行)——動機是把「規格閘留痕不算」這條篩選邏輯單一化,立意是對的。但這個整併只統一了**邏輯**,沒有處理**呼叫端**:凡是原本「先呼叫 `_review_loop_ids` 再呼叫 `_escape_review_rows_by_loop`」的地方,現在等於連續呼叫兩次同一支函式,`.canary-log.jsonl` 被整檔讀取、逐行 `json.loads` 兩遍——ledger 越長,這個浪費越明顯(repo 現有的 `.canary-log.jsonl` 已經上千行)。

除了 `_escape_stats`(F1 已指出的 9896/9897 行)之外,單一次手動記帳 `lumos loop escape <迴圈> --stage ... --sha ...` 也一樣重掃:第 9738–9752 行手寫了一段迴圈算 `known`(驗證迴圈編號存不存在),第 9788 行又呼叫 `_review_loop_ids(env)` 算 `rec["loop_kind"]`,兩次各自完整讀一次 `.canary-log.jsonl`,而且都在寫入鎖(9793 行 `with _vault_write_lock`)**之外**——也就是說中間如果有別的行程對 `.canary-log.jsonl` 追加了一筆新的審查紀錄,`known`(判斷編號存不存在)跟 `_review_loop_ids`(判斷歸哪一類)看到的可能不是同一份帳。

重現(數實際讀檔次數,不用猜):

```
cd /private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/ba2fc358-b2c4-4fe8-b8cf-9883c1468562/scratchpad/escimpl/exp2-併發/repo
python3 - <<'EOF'
import importlib.machinery, importlib.util
loader = importlib.machinery.SourceFileLoader("m", "scripts/lumos")
spec = importlib.util.spec_from_loader("m", loader)
m = importlib.util.module_from_spec(spec)
loader.exec_module(m)

import tempfile, json, sys, io, contextlib
from pathlib import Path

d = Path(tempfile.mkdtemp())
vault = d / "vault"; vault.mkdir(); (vault / "Projects").mkdir()
canary = d / ".canary-log.jsonl"
canary.write_text(json.dumps({"kind":"none","loop":"甲","round":"r1","tier":"standard","token":"X1"})+"\n", encoding="utf-8")

orig = Path.read_text
counts = {}
def counting(self, *a, **kw):
    counts[str(self)] = counts.get(str(self), 0) + 1
    return orig(self, *a, **kw)
Path.read_text = counting

sys.argv = ["lumos", "--vault", str(vault), "loop", "escape", "甲", "--stage", "CI", "--severity", "major", "--desc", "d", "--sha", "x1"]
with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
    rc = m.main()
print("rc:", rc, "  canary-log 被讀了幾次:", counts.get(str(canary)))
EOF
```

實跑輸出:`rc: 0   canary-log 被讀了幾次: 2`——單獨一次記帳指令,`.canary-log.jsonl` 被完整讀、解析兩遍。同段程式碼的 `_escape_stats`(F1)也是兩遍,`escape-log` 也是兩遍(見 F1 指令),同一種「共用掃帳函式各處各自呼叫、沒有在單次請求裡共用一份結果」的形狀在這支檔案裡至少出現三處,r2 只解決了「同一個迴圈的每一列逃逸都重讀計劃」(patch 裡 `_cat_cache` 那段,r1 併發席已折的那條),沒有處理「同一次呼叫裡兩本帳各被整檔重掃」這條。

已看,無:計劃第一節新增的「列上已記 `loop_kind` 為準」規則(patch 第 9 行)與 `_escape_row_bucket` 的實作(patch 第 241–255 行)本身邏輯一致,沒有額外併發疑慮;`_escape_withdraw` 在鎖內只呼叫一次 `_escape_raw_rows`(第 9605 行),鎖內沒有重複讀帳,token 重複檢查(`len(hits) > 1`)與後續撤回紀錄的寫入都在同一把鎖、同一份 `rows` 快照裡完成,沒有 TOCTOU;`--repo` 併入撤回互斥檢查(patch 第 78–84、133–136 行)與 `_plan_for_loop` 的路徑字元擋法(patch 第 73–74 行)都是同步、無競態的純檢查,沒有問題。
