severity: major

## F1 健檢產生的 CI 範本不是合法 YAML

severity: major
blocking: 是
引句:「+  (checkout 要設 fetch-depth: 0。回傳碼照原樣讓這步紅綠:0 是沒有要處理或 warn 模式只印;1 是 block 模式擋下;」
file: `scripts/lumos:28443`

1. `_DRIFT_CI_STEP` 把兩行說明文字直接接在 CI 步驟後，隨後又串接 `_CI_PY314_NOTE`；三行都沒有 `#`，消費專案照完整健檢提示貼入 workflow 後會變成 YAML 內容。

2. 最小翻紅重現：

```sh
PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3 -c \
'import runpy; m=runpy.run_path("scripts/lumos"); print("jobs:\n  demo:\n    runs-on: ubuntu-latest\n    steps:" + m["_DRIFT_CI_STEP"] + m["_CI_PY314_NOTE"])' |
ruby -e 'require "yaml"; begin; YAML.safe_load(STDIN.read, aliases: true); puts "PASS"; rescue => e; warn "FAIL: #{e.class}: #{e.message}"; exit 1; end'
```

輸出與退出碼：

```text
FAIL: Psych::SyntaxError: (<unknown>): could not find expected ':' while scanning a simple key at line 19 column 3
rc=1
```

3. 新測試只抽出 `run: |` 底下的 shell body 執行，遇到縮排較淺的說明行便停止，因此沒有驗證健檢實際輸出的完整 YAML。

## F2 `before` 遺失時 CI 只檢查最後一個提交

severity: major
blocking: 是
引句:「+            BEFORE="$(git rev-parse -q --verify "$SHA^1^{commit}" 2>/dev/null || git hash-object -t tree /dev/null)"」
file: `.github/workflows/ci.yml:166`

1. 新分支首推或強推後舊頂端不存在時，程式把起點固定成 `SHA^1`。一次推送包含多個提交時，前面的提交完全不在 `drift check` 範圍內；若狀態翻轉發生在那些提交、最後一個提交無關，block 模式也會錯誤放行。健檢範本在 `scripts/lumos:28452` 複製了同一算法。

2. 用本次真實四提交歷史套入新分支首推輸入，以下檢查翻紅：

```sh
base=618ee85f
sha=dca86f7d
before=0000000000000000000000000000000000000000

if [ "$before" = 0000000000000000000000000000000000000000 ]; then
  before="$(git rev-parse -q --verify "$sha^1^{commit}" 2>/dev/null ||
            git hash-object -t tree /dev/null)"
fi

echo "expected=$base..$sha"
echo "actual=$before..$sha"
echo "expected_count=$(git rev-list --count "$base..$sha") actual_count=$(git rev-list --count "$before..$sha")"
test "$(git rev-list --count "$before..$sha")" -eq "$(git rev-list --count "$base..$sha")"
```

輸出與退出碼：

```text
expected=618ee85f..dca86f7d
actual=61e30a3afe6aab055e17c0f9907a83ec4ff945f1..dca86f7d
expected_count=4 actual_count=1
rc=1
```

3. 測試目前只斷言退到第一個父提交，沒有造「首推／強推一次帶多個提交，漂移發生在倒數第二個以前」的反例。

## 圖譜鏡頭逐條判定

1. `Issues/code-loop守衛main-direct盲區`：既有 code-loop 仍使用每個推送 ref 的 `_range`，本次新增的 drift 段排在其後，沒有讓該盲區復發。
2. `Systems/存量漂移守衛`：F1 破壞「doctor 給消費專案貼的 CI 步驟」；F2 使新分支與遺失舊頂端的多提交推送只覆蓋最後一個提交。
3. `Systems/每支檔有家`：本次沒有改 home check 判定；另開 Issue 記錄的既有範圍問題不由這段 drift 邏輯擴大。
4. `Systems/筆記內容閘`：note-shape 本體及回傳碼處理未改，新增範圍函式只供 drift 使用。
5. `Systems/測試假綠形態`：現有測試確實執行 shell body，但沒有驗完整健檢 YAML，也沒有驗多提交首推的覆蓋範圍；兩個缺口分別對應 F1、F2。
6. `Systems/anchor-integrity`：兩支受保護檔的 baseline 已同步更新，未見漏更新或旁路。
7. `Systems/lumos-cli-lifecycle`：沒有改 re-inject 或 sentinel 外內容，該合約不受影響。
8. `Systems/lumos-cli-read`：沒有改 search 的 superseded/stale 過濾；doctor 新提示不碰該讀取合約。

最高等級:major