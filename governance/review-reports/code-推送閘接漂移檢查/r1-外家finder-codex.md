severity: major

## F1 CI 把 `2` 與其他非零碼也判紅，違反只有 `1` 擋下的合約

severity: major

blocking: 是

引句:「python scripts/lumos drift check --diff "$BEFORE..$SHA" --repo . || {」

file: `.github/workflows/ci.yml:162`  
file: `scripts/test_lumos.py:51112`

1. 以假 `python` 讓 drift check 分別回 `0/1/2/7`，原樣執行新增的 CI 控制流：

```sh
for rc in 0 1 2 7; do
  FAKE_RC="$rc" bash -c '
    python(){ return "$FAKE_RC"; }
    BEFORE=abc SHA=def
    python scripts/lumos drift check --diff "$BEFORE..$SHA" --repo . || {
      got=$?
      if [ "$got" -eq 1 ]; then exit 1; fi
      exit "$got"
    }'
  echo "drift=$rc ci=$?"
done
```

輸出：

```text
drift=0 ci=0
drift=1 ci=1
drift=2 ci=2
drift=7 ci=7
```

2. `exit "$rc"` 讓所有非零碼都使 GitHub Actions 失敗；正確矩陣應是 `0→0、1→1、2→0、其他→0`。
3. 新測試反而把錯誤行為釘住：說明寫「只有 rc1 讓 CI 紅」，斷言卻要求 `{"0":0,"1":1,"2":2}`。因此參數錯誤或工具異常會阻斷主線，且既有測試仍顯示通過。

## F2 CI 遇到全 0 或不存在的 `before` 時會在漂移核心之前直接放行

severity: major

blocking: 是

引句:「# lumos 從跟主線的分岔點算(同 note-shape 那步,前一版原樣交給它)。模式照被推送頂端提交的 .lumos/config.json」

file: `.github/workflows/ci.yml:138`  
file: `.github/workflows/ci.yml:151`  
file: `scripts/lumos:25784`  
file: `scripts/lumos:33039`

1. 前一個 CI 步驟先 fetch，使正常配置下的 `main@{upstream}` 指向本次已推送的 `SHA`。
2. `before` 為全 0，或 force push 後舊提交不存在時，`_lens_push_base` 檢查 `tip` 是否已在 upstream；此時比較的是 `SHA` 對同一個 `SHA`，必然回傳 `base=None`。
3. `_note_audit_resolve` 隨即回 0，`_drift_check_core` 完全不執行。以下唯讀探針對兩種輸入都翻紅：

```sh
for b in \
  0000000000000000000000000000000000000000 \
  deadbeefdeadbeefdeadbeefdeadbeefdeadbeef
do
  GIT_CONFIG_COUNT=2 \
  GIT_CONFIG_KEY_0=branch.main.remote GIT_CONFIG_VALUE_0=. \
  GIT_CONFIG_KEY_1=branch.main.merge GIT_CONFIG_VALUE_1=refs/heads/main \
  python3 -c '
import runpy, sys
m = runpy.run_path("scripts/lumos", run_name="lumos_review")
tip = m["_lens_full_sha"](".", "HEAD")
base, why = m["_lens_push_base"](".", sys.argv[1], tip)
print(f"before={sys.argv[1][:12]} base={base} why={why}")
assert base is not None, "drift core will be skipped"
' "$b"
done
```

輸出：

```text
before=000000000000 base=None why=新分支首推,而且頂端已在主線(main@{upstream})上——沒有新東西
AssertionError: drift core will be skipped
before=deadbeefdead base=None why=起點在本機找不到,而且頂端已在主線(main@{upstream})上——沒有新東西
AssertionError: drift core will be skipped
```

這使首次 push 或舊 `before` 未被 checkout 取回的 force push 沒有 CI 漂移後盾；新增測試只驗「40 個 0 有傳給 CLI」，沒有驗核心確實被執行。

## 邊界走查

- 刪除 ref：hook 在 `local_sha` 全 0 時於迴圈開頭跳過；CLI 本身也把終點全 0 判為沒有新樹，回 0。
- 新分支：pre-push 原樣傳全 0；遠端主線仍是舊值時，實跑會從分岔點計算。CI 已更新 upstream 的情況則命中 F2。
- tag：非分支只把 code-loop 改成 advisory，後面的 drift check 仍執行；輕量 tag SHA 可直接解析，帶註解 tag 會以 `^{commit}` 剝到提交。
- force push：舊 SHA 尚在本機時直接比較舊值與新值；舊 SHA 不存在時，CI 命中 F2。
- shallow clone：在解析範圍前回 0，記 `skipped-env`；符合既定降級語意。
- 沒有 vault：列完頂端樹後印「沒有圖譜」並回 0。
- `GRAPHCTL` 不存在：pre-push 在進入所有閘前整支回 0；這是既有、明示的降級路徑。
- pre-push 退出碼矩陣實測為 `0→0、1→1、2→0、7→0`，符合本次規格。
- `LUMOS_SKIP_DRIFT_CHECK`：只有字面值 `1` 走略過；`0/true/01/yes` 均繼續檢查。
- CI 退出碼與 `before` 邊界分別由 F1、F2 擋住放行。

## 圖譜鏡頭逐條判定

- `Issues/code-loop守衛main-direct盲區`：pre-push 仍使用 stdin 的逐-ref 範圍，未重引入原本 main-direct 空 diff；F2 是 CI 端相似的推送起點盲區。
- `Systems/存量漂移守衛`：F1 破壞「只有 rc1 判紅」，F2 破壞全 0／缺起點時由主線分岔點計算的宣稱。
- `Systems/每支檔有家`：既有 home check 的範圍與順序未改，不受影響。
- `Systems/筆記內容閘`：note-shape 本身未改；但它先 fetch 主線的副作用會觸發 F2。
- `Systems/測試假綠形態`：新增測試同時命中「判準與說明矛盾」及「只驗參數有傳、沒驗核心有跑」兩型。
- `Systems/anchor-integrity`：pre-push 與測試檔雜湊已同步更新，未見基準漏改。
- `Systems/lumos-cli-lifecycle`：hook 仍位於既有 vendored 目錄，未碰 re-inject sentinel 外內容；分發合約未破壞。
- `Systems/lumos-cli-read`：搜尋與 superseded/stale 過濾路徑未改，不受影響。
- 其餘只列名節點：bound-tests 與 test-layers 的相對順序仍保留；canary、design-loop、guard-kill、slim、雙向門、逃逸帳、deinit、cochange、節點範圍及不可逆檢查均無直接行為改動。

語法檢查結果：`bash -n scripts/hooks/pre-push` 與兩支 Python 檔的 AST 解析皆通過。完整新增測試因唯讀沙箱禁止 `mktemp` 無法啟動；上面兩項均改用不落盤探針重現。

最高等級:major