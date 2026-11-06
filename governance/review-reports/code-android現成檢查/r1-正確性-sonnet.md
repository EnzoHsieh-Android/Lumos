severity: major

審查範圍:逐 hunk 讀完 `r1-snapshot-甲乙.patch`,在 `android-blind-judge` 的 `cafcd3ece` 上實跑。`-k android_ci`(38 項)、`-k detekt_compose`(8 項)、`-k detekt_shared`(7 項)、`-k kt_catalog_batch4`(12 項)全綠。`scripts/lumos` 一 import 就會跑主程式,所以 A1、A3 的行為是把函式原文抽到 `/tmp/lumos-seat-work/code-android現成檢查/正確性-sonnet/` 的獨立腳本裡跑。

## F1 A3 展開 `$HOME` 沒有任何測試守,改壞照綠
severity: major
blocking: 是

file: `scripts/lumos:39044`(`_lint_android_ci_advisories` 呼叫 `_android_plugin_paths`,後者做 `$HOME`、`${HOME}` 展開)。
計劃範圍 3 的 A3 寫明「展開 `$HOME`」。型錄範本與 `compose.yml` 檔頭的真實寫法就是 `--plugins $HOME/.local/share/lumos/detekt-plugins/detekt-compose-0.4.28-all.jar`。

`t_lint_android_ci_advice` 的 A3 案例用的全是 `tempfile.mkdtemp` 產生的絕對路徑,見下面引句。整支測試沒有 `$HOME`、`${HOME}`、`~`、`-p`、`--plugins=`、逗號多支的案例。

引句:「jar = Path(tempfile.mkdtemp(prefix="gctl-andci-jar-")) / f"detekt-compose-{ver}-all.jar"」

合理的改壞:把 `.replace("$HOME", str(Path.home())).replace("${HOME}", str(Path.home()))` 整段拿掉。重現是對抽出的函式跑同一條範本命令:
- 現況:回 `['/Users/enzo/.local/share/lumos/detekt-plugins/detekt-compose-0.4.28-all.jar']`。
- 拿掉展開後:回 `['$HOME/.local/share/lumos/…']`,`Path(...).is_file()` 為 False。

後果是每個照範本接好、外掛檔也在的專案,都會被印 A3「外掛檔不在」。這個改壞與測試 S2 的條款,現有測試都抓不到。

## F2 A1 字面判斷漏報:註解行、`-x lint`、鬆散的 `gradle ` 字樣
severity: minor
blocking: 否

file: `scripts/lumos:39002`(`_android_ci_has_lint_task`)。
引句:「if not re.search(r"gradlew|\bgradle[ \t]|\barguments:", line):」

這個函式沒有去掉註解、也沒有看 `-x` 排除。下面幾個輸入實測都回 True,等於沒接卻不印 A1:
- `# ./gradlew lintDebug later`:有人把 lint 步驟註解掉,A1 反而安靜。
- `./gradlew build -x lint` 與 `assemble -x lintDebug`:明確排除 lint,卻算接上。
- `echo gradlew build later` 與 `echo 'gradle check passed'`:只是 echo。
- `./gradlew test --tests check`。
- `detekt check`:這行有 gradlew 字樣,`check` 不是 lint 任務。

計劃把「只看字面」列為代價,所以只列 minor。其中註解行最容易發生,測試沒有案例。

## F3 A1 字面判斷誤報:多行寫法、矩陣變數、變體前綴撞名
severity: minor
blocking: 否

file: `scripts/lumos:39002`。實測回 False,也就是已經接了 lint 卻印 A1 的輸入:
- 行尾反斜線續行:`./gradlew \` 下一行才是 `lintDebug`。任務詞那行沒有 `gradlew`,被略過。
- `setup-gradle` 的 `arguments: |` 多行區塊,`lintDebug` 在後面獨立一行。測試只有單行的 `arguments: lintDebug`。
- `./gradlew ${{ matrix.task }}`,任務在 `matrix: task: [lintDebug, test]` 裡。
- 變體前綴撞名:`lintFixtureDebug`、`lintReportingDebug`、`lintVitalityDebug`、`lintFixedDebug` 都被當成 `Fix`、`Report`、`Vital` 開頭而跳過。

計劃只承認「任務包在 shell 腳本或 composite action」會誤報,上述寫法不在其中。這些寫法在真實 CI 很常見,而且沒有關掉提醒的辦法。

## F4 A3 路徑解析:相對路徑、環境變數、`sh -c` 包裝
severity: minor
blocking: 否

file: `scripts/lumos:39044`。引句:「if not Path(pth).is_file():」
- 相對路徑依目前工作目錄判斷,不是 `repo_root`。`lumos lint-check --repo X` 從別的目錄跑時,`./p/a.jar` 會誤報不在。
- `-p $XDG_DATA_HOME/a.jar` 實測回 `['$XDG_DATA_HOME/a.jar']`,只展開 `$HOME`,其他環境變數照原樣,所以一定誤報。
- `sh -c 'detekt --plugins $HOME/a.jar'` 實測回 `[]`。`lint-check` 的格式檢查明文接受這種包裝(S7 有測),A3 卻漏看。
- 兩條命令指到同一支不存在的檔,會印兩行重複的 A3。

## F5 測試沒守到的計劃條款
severity: minor
blocking: 否

file: `scripts/test_lumos.py` 的 `t_lint_android_ci_advice`。計劃寫明但測試沒有案例的條款:
- 隱藏資料夾不進(`not d.startswith(".")`)。
- 不跟符號連結進資料夾(`followlinks=False`)。
- 每支最多讀 1 MB。
- `settings.gradle` 與 `gradle/libs.versions.toml` 納入掃描。
- `bitrise.yml`、`.circleci/config.yml`、`Jenkinsfile`、`azure-pipelines.yml` 只測了 `.gitlab-ci.yml`。

把任一項拿掉,測試照綠。這些守的是範圍界線,影響較小,所以只列 minor。

## manifest 逐條判定
- `scripts/lumos:38995` 的 `open(` 資源題:誤報。diff 裡 `_android_build_texts` 用 `with open(root / rp, "rb") as fh:`,離開區塊就關。`_ci_config_texts` 用 `read_text`,沒有手動開檔。

## 其他檢查結果(不影響)
- T4 改用 `_ci_config_texts(repo_root, github_only=True)`:檔案範圍、排序、`errors="replace"` 都跟舊版一致,判定不變。測試 502 行只驗了檔案範圍,等價性看程式碼成立。
- S4 口徑:型錄 473 列,`t_kt_catalog_batch4_wiring` 通過。
  - 我另外重算了一次,沒有口徑函式與型錄對不上的列。
  - 仍標「批四(現成規則)」的 76 列,規則欄不是全預設關就是沒有 Android Lint 或 cr 規則碼。
  - 有 Lint 或 cr 規則碼卻標「批一」的 10 列,是測試刻意跳過的非第四批列。
- 掃建置檔的深度、檔數上限和 `build/` 排除都有測試守,我逐一對過,邏輯沒問題。
- CI 步驟:
  - `RUNNER_TEMP/detekt` 目錄由前一步建立。
  - 外掛 jar 的 sha256 與本機實測一致(`b8c732…ddd6`)。
  - 純文件推送的子集跑法不裝 detekt,也不跑這支測試。
- 圖譜五篇:
  - `lint-declaration-health` 的「另起一則」WHY 與實作相符,T4 判定不變,所以不影響。
  - `linter精選目錄` 第 158、181 行與實作一致,不影響。
  - `bound-tests-gate` 的 ★INVARIANT★ 不被觸及,不影響。
  - `kotlin規則包`、`pitfalls-code-loop` 在這份 diff 沒有被觸及的行為,不影響。

## 總結
總結:最嚴重是 major,會擋 1 條(F1),其餘 F2 到 F5 不擋。
