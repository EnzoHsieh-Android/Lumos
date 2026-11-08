severity: minor

我查完五項正確性疑點，沒有找到會讓 CI 判錯或工具沒裝上的問題。另外有一條 minor 的覆蓋缺口，列在後面。

## 逐項查過

1. **複合動作語法**:三個步驟都有 `shell: bash`,符合官方對 composite run 步驟的要求。
   引句:「    shell: bash」
   - `$RUNNER_TEMP` 是 runner 預設環境變數,composite 步驟裡讀得到。
   - 步驟層級的 `env:` 在 composite 裡合法。
   - 寫進 `$GITHUB_PATH` 與 `$GITHUB_ENV` 的內容,會在呼叫它的工作的後續步驟生效。
   - 我沒有實際在 GitHub 上跑,以上是依 GitHub 對 composite action 的官方規格判斷。
   - 測試端讀 `LUMOS_DETEKT_COMPOSE_JAR` 的位置是 `scripts/test_lumos.py:128922`。detekt 與 ast-grep 靠 PATH 找,見 `scripts/test_lumos.py:126537`。兩者在文件子集那步都拿得到。
   引句:「      echo "LUMOS_DETEKT_COMPOSE_JAR=$j" >> "$GITHUB_ENV"」

2. **本地動作的前提**:prep 與 shards 在 `uses: ./.github/actions/test-tools` 之前都已經 `actions/checkout@v4`,本地動作讀得到。
   引句:「        uses: ./.github/actions/test-tools」
   - file: `.github/workflows/ci.yml:44-48`(prep 的 checkout,取自本 repo 的 ci.yml)。

3. **prep 用的 python 來源**:prep 的 `actions/setup-python@v5`(3.14)在新步驟之前,所以 `python -m pip install ast-grep-cli==0.51.1` 用的是 setup-python 的 python。
   - 它的 bin 在 PATH 上,`which("ast-grep")` 找得到。
   引句:「    run: python -m pip install --quiet ast-grep-cli==0.51.1」
   - file: `.github/workflows/ci.yml:63-65`

4. **條件**:
   - prep 的 `suite` 只有在 push 事件、`before` 有效、lumos 判出 docs 時才是 docs,其餘一律 `full`,見 `[ "$suite" = docs ] || suite=full`。PR 事件與首推都是 full。
   - 所以 prep 跑文件子集時一定帶著 `suite == 'docs'`,不會出現「prep 跑文件子集卻沒裝」。
   - full 時改由 shards 裝。
   - `gates` 工作不跑 `test_lumos.py`(只跑自主迴圈測試與 doctor),不需要這些工具。
   引句:「        if: steps.suite.outputs.suite == 'docs'」

5. **新增的撈 ✗ 那段**:`grep ... | tail -40 || true` 沒撈到時不會讓步驟提早結束,也不會把綠判成紅。
   - 該步沒指定 `shell:`,是 `bash -e` 且沒有 pipefail,管線的結束碼本來就是 `tail` 的 0,`|| true` 又多一層保險。
   - 最終 `exit $rc` 才決定紅綠,不受 grep 影響。
   - 測試輸出的失敗行確實以 `  ✗ ` 開頭,見 `scripts/test_lumos.py:178`。
   引句:「            grep -nE "^  ✗|EXCEPTION" "/tmp/shard-$i.log" | tail -40 || true」

6. **既有測試**:
   - `t_ci_yml_matrix_and_gates_shape` 依 `^  <job>:` 切工作,檢查的是 fetch-depth、timeout、matrix、gates 的指紋。拿掉 shards 裡三個安裝步驟不影響它。
   - `scripts/test_lumos.py` 裡沒有測試去找 ci.yml 內的 `DETEKT_SHA256`、`ast-grep-cli` 或 `COMPOSE_RULES` 字樣(grep 確認),沒有「守衛照綠但沒守到」的舊守衛。
   - 其他讀 ci.yml 的測試(`t_secev_s32_ci_tag_job` 等)看的是 `security_tag` 與 `prep` 的 `if` 行,沒被動到。
   引句:「 `t_ci_yml_matrix_and_gates_shape` 守 1..N 各一次」

7. **圖譜鏡頭**:
   - `Systems/canary-audit` 的兩條合約(canary record 落盤、second 不影響 gate)只因為間接牽連 ci.yml 才被列出,與安裝步驟無關,不受影響。
   - `Systems/lumos-cli-lifecycle` 的 re-inject 合約是 CLAUDE.md sentinel 以外內容 byte-equal,CI 安裝步驟碰不到,不受影響。
   - 表態記錄全是 `na`,這次 diff 沒有 Python 程式變動,不矛盾。
   - `bound-tests-gate` 新增的 PITFALL 帶 `[repro:]`,符合格式。`about_code` 與 `responsibility` 也有補。
   引句:「  - .github/actions/test-tools/action.yml」

## 發現

1. `.github/workflows/ci.yml:73`(prep 的 uses 行)
severity: minor
   blocking: 否
   情境:沒有任何測試斷言「prep 在 `suite == docs` 時 `uses` 這個動作」或「shards `uses` 這個動作」。
   - 如果日後有人把 prep 那三行刪掉,或把 `if` 條件改錯,本機和推送前的全套測試都綠。
   - 只有下一次純文件推送上 CI 才紅,也就是這次要修的事故會原樣重演。
   - 這次修法等於由 CI 自己當驗證。
   - 補一條測試即可,例如斷言 prep 區塊含 `uses: ./.github/actions/test-tools` 且帶 `suite == 'docs'`,shards 區塊也含它。
   引句:「        uses: ./.github/actions/test-tools」
   佐證:`scripts/test_lumos.py:88692`(`t_ci_yml_matrix_and_gates_shape` 只守 fetch-depth、matrix、gates,不看安裝步驟)

總結:最高等級 minor,blocking 0 條。
