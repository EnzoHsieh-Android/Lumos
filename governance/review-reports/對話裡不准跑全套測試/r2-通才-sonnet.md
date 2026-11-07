severity: blocker

## F1 `--lf` 沒進 `_fanout_wanted` 的條件清單,在對話裡下 `--lf` 會跑出全套
severity: blocker
blocking: 是(擋下訊息主推的指令真的會跑全套,擋的目的整個落空)

- 段落:做 1(「用真值判斷,跟 `_fanout_wanted` 同一口徑」)、做 5(新增 `--lf`)、S5。
- 問題:做 1 放行 `--lf`,放行後接著執行 `if _fanout_wanted(_args):`。現行 `_fanout_wanted` 只把 `keyword`、`shard`、`suite`、`list`、`serial`、`exitfirst` 當條件,沒有 `lf`。所以單帶 `--lf` 時,`_fanout_wanted` 回 True(片數預設 4),`_fanout_main` 會把全套切成 4 片跑。`_fanout_main` 轉給子程序的只有 `--seed`、`--keep-tmp`、`--ff`,不含 `--lf`。
- 後果:在對話裡照擋下訊息建議打 `python3.14 scripts/test_lumos.py --lf`,會在放行之後跑出約 4 分鐘的全套。推送前閘提示的 `--lf -x` 因為帶 `-x` 會走單一程序,沒這問題。
- 規格缺口:「做」八條只改了判斷函式、插入點、`--lf` 旗標與 pre-push 提示,沒寫要改 `_fanout_wanted`。S5 只驗「只跑那 2 支」,沒指定用預設切片的環境真跑,抓不到這條。
- 佐證:
  引句:「沒帶條件:`args.keyword`(合併位置參數後)、`args.suite`、`args.list`、`args.lf` 全是假值」
  file: `scripts/test_lumos.py:49391-49398` 的 `_fanout_wanted` 回傳式裡沒有 `args.lf`。
  file: `scripts/test_lumos.py:49470-49474` 的 `extra` 沒帶 `--lf`。

## F2 做 2 的三成判斷沒講分母與位置,`--shard` 和 `--list` 兩條路有歧義
severity: minor
blocking: 否(不影響主路徑,而且推送前閘與切片子程序本來就豁免)

- 段落:做 2、做 3。
- 問題一:現行 main 是先切片(`--shard`),再套 `-k`。「超過全部測試的三成」若用切片後的清單算,`-k t_ --shard 1/4` 只佔約 25%,不會被擋。規格沒說分母是篩選前的全部測試。
- 問題二:規格說第 2 條接在「測試清單篩選完、開始跑之前」。現行 `--list` 在篩選完之後、`return 0` 之前就返回。如果判斷放在 `--list` 分支之前,`--list -k t_` 會被擋,跟 S1「`--list` 不擋」的精神不一致;放在之後則是死碼。規格沒指定。
- 佐證:
  引句:「第 2 條接在測試清單篩選完、開始跑之前」
  file: `scripts/test_lumos.py:49775-49790`(`--list` 分支)與 `scripts/test_lumos.py:49715-49745`(`--shard` 區塊在 `-k` 之前)。

## F3 判斷函式回傳值裝不下逃生門放行的訊息與計數
severity: minor
blocking: 否(實作時一定會補,但驗收條款目前沒有可驗的形狀)

- 段落:做 1(「回擋下訊息或 None」)、做 6、做 7、S2 與預期值表。
- 問題:函式只回「擋下訊息或 None」,逃生門放行時也回 None,呼叫端分不出「根本不用擋」和「本來會擋、靠逃生門放行」。做 6 要求只在後者印「對話裡放行跑全套」並計數。S2 預期值表寫的是「不擋,印放行與理由」,但 S2 的測試對象是判斷函式。規格沒說印與計數是函式的副作用,還是 main 另算一次。
- 若是函式的副作用:單元測試會寫計數檔,而且與「判斷函式」的純函式描述矛盾。
- 佐證:
  引句:「回擋下訊息或 None。在對話裡(`env.get("CLAUDECODE") == "1"`)」
  引句:「算數時只在「本來會擋」的情況印一行「對話裡放行跑全套,理由:<理由>」」

## F4 `--lf` 讀的「上次紅」紀錄會過期,而且在消費專案永遠是空的
severity: minor
blocking: 否

- 段落:做 5、做 1 擋下訊息(推薦 `--lf`)、「實務隱患」消費專案那條。
- 問題一:現行讀取是把 `.lumos/test-cache*.json` 全部 glob 起來聯集。不分片的跑法只覆寫 `test-cache.json`,各片的 `test-cache-shardXofY.json` 不會被清。
  - 例:推送前閘紅了,各片檔留著紅名單;改好後用 `--lf -x` 跑到綠,只清掉 `test-cache.json`。下次 `--lf` 仍會重跑各片檔裡已經修好的舊紅。
  - `--lf -x` 還會讓 `test-cache.json` 只記「停在第一支紅」那一支,跟「上次所有紅」不是同一回事。規格拿 pytest 的 `--lf` 當依據,沒處理這個差異。
- 問題二:這份紀錄只在 `_is_src`(來源 repo)時才讀寫。消費專案收到的擋下訊息一樣推薦 `--lf`,但那邊 `--lf` 永遠回「沒有紀錄,rc 2」。
- 佐證:
  file: `scripts/test_lumos.py:49746-49762`(`_is_src` 才 glob 讀)。
  file: `scripts/test_lumos.py:49850-49855`(只寫自己那份 cache 檔)。
  引句:「消費專案**:測試總檔會被安裝進消費專案(工具自裝檔),那邊在對話裡不帶條件跑也會被擋,跟本 repo 一致。」

## 已讀,無 finding 的部分
- 前言與 frontmatter、PRIOR-ART、RETIRE-IF:`scripts/scenario_probe.py:1162` 確有 `env.pop("CLAUDECODE", None)`,`scripts/hooks/pre-push:393` 確有 `export LUMOS_PUSH_ATTEMPT`,先例宣稱屬實。
- 跟舊決定的關係、範圍「不做」、依據來源、回退、天花板:內部一致。交叉引用的 `Projects/測試總檔預設切片_計劃`、`Systems/測試執行器`、r1-intake.md 都找得到。
- pre-push 的「下一步」提示確實有兩處(`scripts/hooks/pre-push:1032` 與 `:1035`),跟「兩處」吻合。
- 推送前閘的各片與 `--suite` 子集都在 `export LUMOS_PUSH_ATTEMPT` 之後才起,所以對話裡 `git push` 觸發的閘不會被擋。
- CI 的 `.github/workflows/ci.yml` 起 shard 的呼叫都帶 `--shard`,而且 CI 沒有 `CLAUDECODE`,不受影響。

## 實務隱患鏡頭(逐類)
- 金流:無,不碰付款。
- 對外送出:無,不連網、不呼叫外部服務。
- 不可逆:無,只動執行器入口與提示文字,計數檔在工作目錄外,退提交即回原狀。
- 守衛面:有。這是新擋停,F1 就是這一類:放行路徑(`--lf`)反而開出全套。兩個豁免標記與逃生門都是環境變數,規格「天花板」第 2 點已承認。
- 子程序繼承:`CLAUDECODE` 在判斷後才從 `os.environ` 拿掉。現行測試檔裡沒有其他地方讀它(只有 `scenario_probe.py`),我沒看到副作用。

## 固定席逐條判
- `測試假綠形態` 的 INVARIANT(還原翻紅釘要配前置斷言):S4 已有「前置:拿掉 `CLAUDECODE` 時回 None」。S5 沒有對應前置,測不到 F1。不破壞該合約,但 S5 要補預設切片環境的前置,才能抓 F1。
- `bound-tests-gate` 的 INVARIANT(逐支真跑綁定測試):閘用 `-k` 帶具體測試名,不是全套,不會被新守衛擋,判「不影響」。
- 其餘固定席(`lumos-cli-lifecycle`、`design-loop`、`canary-audit`、`lumos-cli-read`、`guard-kill`、`codex-harness`):合約都不涉及執行器入口參數或環境變數,判「不影響」。

總結:最高等級為 blocker,blocking 共 1 條。
