severity: minor

# CI 加速 r1 正確性審查(外部第三方立場)

## 逐情境走查結論

- ① push 全套:prep 輸出 suite=full,shards 四台各跑兩份(1 2/3 4/5 6/7 8,SHARD_TOTAL=8,1..8 各一次),gates 同時跑七道後盾。通過。
- ② push 純文件:prep 內跑文件子集(`--suite docs`,4 片寫死 i/4,與原本同),shards 因 `needs.prep.outputs.suite == 'full'` 不成立而 skipped(skipped 不使整個 run 紅),gates 以 SUITE=docs 跑 `-k real_claude_md`。通過。
- ③ pull_request:before 為空,suite=full;各工作都有補本機 main 那步;push 專屬四步被 `if: github.event_name == 'push'` 擋掉,行為與原本一致。通過。
- ④ prep 某步紅:shards、gates 因 needs 預設要 prep 成功而 skipped,整個 run 紅;原本單一工作前步紅也是後面全不跑,等價,不算退步。
- ⑤ 單台 matrix 紅:`fail-fast: false`,其餘台跑完,shards 工作判 failure,run 紅;gates 與 shards 無依賴,照跑。通過。
- ⑥ 分份編號:已用 ruby 解析 yaml 確認 matrix 為 ["1 2","3 4","5 6","7 8"],對 SHARD_TOTAL "8" 剛好 1..8 各一次;`--shard` 對 i/8 的合法範圍檢查在 scripts/test_lumos.py 的 `--shard` 參數處理(1..n),8 合法。
- ⑦ 失敗片段列印:迴圈從 `1 2 3 4` 改為 `$MY_SHARDS`(bash 對不加引號的變數切詞,"1 2" 會展開成兩個編號)、log 路徑 `/tmp/shard-$i.log` 每台機器獨立、`|| true` 與 grep 管線原樣保留;`set -u` 下 MY_SHARDS、SHARD_TOTAL 皆有定義。正確。
- ⑧ `permissions: contents: read`:工作流內無任何步驟寫 GITHUB_TOKEN(grep scripts/lumos 與 scripts/test_lumos.py 無 GITHUB_TOKEN/GH_TOKEN 使用,ci 檔只有 checkout、git fetch、git branch、本機 lumos 指令);checkout 的 fetch 與 note-shape 那步的 `git fetch origin` 用 checkout 留下的唯讀憑證即可。⚠ 未實跑 Actions,依 checkout 預設行為推演;驗法:推一次看 gates 的 note-shape 步是否綠。
- 其他:step name 裡的 `${{ env.SHARD_TOTAL }}` 在 `jobs.<id>.steps.name` 允許使用 env context(job 層 env 可用)。舊 job id `test` 改名:`gh api .../branches/main/protection` 回 404「Branch not protected」、rulesets 為空,沒有必要狀態檢查綁舊名;`_ci_failed_step` 以 jobs JSON 取「工作名/步驟名」,會自動帶出 `shards (1 2)/…`。

## Finding 1:指紋不含 env,後盾步驟的 env 被改動時測試不會紅

severity: minor
blocking: 否 + 判準:不會讓現行 CI 出錯,只是測試宣稱「指令逐字相同」但守不到 env 這一類改動,屬守衛的缺口。

引句:「後盾七步全在 gates、指令與拆分前逐字相同、順序相同」
引句:「if _re.match(r"^        \S", ln):」

推演:`_ci_step_fp` 只收 `if`、`continue-on-error`、`run` 三種行;`env:` 區塊(8 格縮排的鍵)落到最後那個分支,被視為結束 run 並丟棄,指紋不計。具體場景:有人把 code-loop gate 的 `LUMOS_SKIP_BOUND_TESTS: "1"` 刪掉,或把 SUITE 那行寫錯成 `${{ steps.suite.outputs.suite }}`(拆分後 gates 裡沒有 id 為 suite 的步驟,值恆為空,純文件推送會改跑自主迴圈整支而非 `-k real_claude_md`,只是變慢),或 note-shape 步的 `BEFORE: ${{ github.event.before }}` 被改掉——七個指紋全部不變、t_ci_yml_matrix_and_gates_shape 仍綠。這次 diff 唯一動到後盾 env 的就是 SUITE 改成 `needs.prep.outputs.suite`,正好落在指紋看不到的地方。拆分前本來就沒這項守衛,所以不是退步;但新測試的名稱與註解把範圍講成「指令逐字相同」,讀者會以為 env 也被守。未實跑翻紅實驗,以程式碼推演。

## 全檔最高結論

引句:「needs.prep.outputs.suite == 'full'」在 shards、`SUITE: ${{ needs.prep.outputs.suite }}` 在 gates,兩處與 prep 的 outputs 對得上,九個情境走完沒有發現漏跑、該紅沒紅或該綠卻紅。

總結:全份最高等級 minor
