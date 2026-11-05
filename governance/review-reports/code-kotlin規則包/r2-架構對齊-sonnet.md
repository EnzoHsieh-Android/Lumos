severity: major

這份 diff 在專案裡新增了一種做法:本機缺外部工具時,用 `_SrcOnly` 走跳過通道。其餘部分(設定讀法、警告、`_stack_changed_ok` 的排除、`configs/` 載入方式)都跟既有做法一致。r1 已報過的 3 條(⊘ 符號、CI 分流、YAML 與表格自寫解析)不重報。

## 問 1:分層與依賴方向

對齊。
- `check.py` 仍是零依賴獨立檔,不 import `scripts/lumos`,沒有跨層直呼。
- `scripts/lumos` 的改動只有兩處:`_lint_new_config` 多一條警告,`_RULEPACK_SAMPLE_RE` 收窄成只認 `.kt`/`.kts`。兩處都在原函式內,沒開新入口。
- 新的 `rules-review/`、`sgconfig-review.yml`、`info` 級只被 `check.py` 的 `CONFIGS` 與 `_DIR_SEVERITY` 消費。新增告警閘宣告的指令只掃 `sgconfig.yml`,所以覆核級不會進閘,依賴方向沒變。

## 問 2:命名與錯誤處理

- 命名對齊:`_files_block_is_test_only`、`_sample_owner`、`SCAN_TIMEOUT`、`REVIEW_FP_PREFIX` 的風格同檔既有常數與函式。
- `lumos` 的設定警告對齊。新警告用 `cfg["warnings"].append(f"設定檔的 lint_new.… 不合法 …")`,跟同函式 `budget_sec` 那幾條同一句式,壞值也是略過並提醒。
- `check.py` 的 `scan`、`loaded_count` 逾時或 OSError 回 None、由上層報「跑不起來」,跟原本非 0/1 退出碼回 None 是同一種處理。`--sg` 缺參數退出碼 2,跟 r1 確認過的 0/1/2 慣例一致。
- 有一處不對齊,見 finding 1。

**finding 1:本機缺外部工具用 `_SrcOnly` 跳過,跟專案已寫明的做法相反。**
severity: major
blocking: 是
引句:「raise _SrcOnly("本機沒裝 ast-grep,這段沒驗到(CI 裝了 0.51.1 會跑)")」
file: `scripts/test_lumos.py:129`
file: `scripts/test_lumos.py:66224`
file: `scripts/test_lumos.py:37440`
file: `scripts/test_lumos.py:49072`
- `_SrcOnly` 的定義(第 129 行起)專指「需要工具鏈來源 repo 才有的產物」,用在消費端必定紅的測試。
- 鄰居 detekt 測試的 docstring 寫明:「本機沒有 detekt 時照實印沒驗到(…_SrcOnly 專指缺來源 repo 的產物,不拿來表示缺外部工具)」。
- 同類的缺外部工具情境,專案既有做法都是「印括號或 ⚠ 提示行再 `return`」(第 37440、66233 行)。
- r1 報的是 ⊘ 提示行與提早 `return` 跟鄰居不同。r2 的修法改走 `_SrcOnly`,新增了第三種處理方式,而且違反上述明文慣例。
- 副作用:`SKIP` 會計入 `EXPECTED_SKIP_MAX`(預設 0,第 126、49072 行)。沒裝 ast-grep 的機器跑全套(`-k` 以外)會因為「跳過數超過上限」被判不過。detekt 路徑不會有這個副作用。
- 建議跟 detekt 鄰居對齊:缺工具時印提示行,並把不需 ast-grep 的靜態檢查照跑。
- 判斷依據是鄰居 docstring 的明文,不是 ⚠。

## 問 3:第二種做法

- 「語意覆核級」不是第二種降級方式。
  - 既有 `report_only`(`scripts/lumos:40081`,`:71967`)指的是新增告警閘裡「命令沒有檔案清單佔位,所以只報不擋」,屬於閘的執行層。
  - 覆核級是規則包內的分級,用目錄加 `sgconfig-*.yml` 加 severity 對應(`_DIR_SEVERITY`),跟已有的 `rules-hints/`、`sgconfig-hints.yml`、`hint` 級是同一種做法,只是多一個目錄。
  - 兩者作用層不同,沒有重疊。
- 唯一的第二種做法是 finding 1。
- `include_test_paths` 的警告與 `_RULEPACK_SAMPLE_RE` 的收窄沿用既有管道,不算第二種。

不對齊共 1 條,其中 major 1 條
