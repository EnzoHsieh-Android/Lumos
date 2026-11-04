severity: major

## 查證摘要(逐項對過)

- **指紋(鏡頭 3)**:我從 patch 還原出 20 個檔,逐檔算 sha256,與 `manifest.json` 全部一致。沒有漏列,也沒有多列。我另外對磁碟上的檔案重算過,結果相同。
- **兩本帳(鏡頭 4)**:patch 裡沒有任何 `-` 行,既有行沒被改動。`.canary-log.jsonl` 的 hunk 是 10 行 context 加 8 行追加,`.governance-log.jsonl` 是 5 行追加。實際 diff 也確認是純追加。新增行裡沒有真實套件名、類別名、路徑或序號。`token` 字串都只是 `SPEC-`、`CANARY-` 的留痕代碼。
- **數字(鏡頭 2)**:
  - 80、14、820/80/7、488 前後一致,都對得上。
  - 七個錯的翻紅支數是 16/2/9/7/5/4/3,收據目標數是 16/2/1/5/5/2/3。`fault-checks/*.json` 的 `targets` 與 `failed_targets` 跟驗證紀錄 S1 表逐格相符。M3 的 9 支與 1 支也對得上,同類別另外 4 支是假實作丟例外。
  - `bad-test-checks` 五組結果(b1、b3、b6、b9 為 survived,b7 為 detected)與 S3 表一致。`fault-matrix-bad-tests.json` 的紅綠分布也與 S3 吻合:b2 只在 baseline 與還原時紅,M1 另外紅 b7。
  - 平板那邊,14 支裝置測試全過,baseline-all 共 15 支,其中 1 支 `useAppContext` 紅。套上 M2 後只跑該類別,14 支裡 1 支紅,都與 S2 相符。
- **裝置序號與型號(鏡頭 1)**:diff 裡沒有裝置序號,也沒有內網 IP、主機名、使用者名、後端網址或金鑰樣式。`SM-X710` 是公開市售型號,可以公開。

## Findings

### 1. 帳內路徑指向的設計審卷證含真實套件名、類別名、方法名
severity: major
blocking: 是

引句:「"snapshot_path": "governance/review-reports/Android單元測試標準實機演練/r1-snapshot.md"」

- **來源**:`.canary-log.jsonl` 新增的 4 行(diff 第 20 到 23 行)把 `report_path`、`snapshot_path` 指向 `governance/review-reports/Android單元測試標準實機演練/`。這個目錄由同一個提交(c08dc36fe)新增,內容沒有去識別化。
- **範圍**:該目錄不在 B 包的檔案裡,只是被帳指到,所以屬於審材外查證。
- **與驗證紀錄的出入**:驗證紀錄只承認留有「少數類別名、方法名(沒有程式碼)」,實際還有真實 applicationId 與 `dev` 變體。

重現指令(搜尋詞換成類別描述,因為本報告也要公開;實際重跑時分別代入考場的套件名片段、被測類別名片段、建議排序號方法名):
```
cd /Users/enzo/harness/lumos-unit-test-drill && grep -nE '<套件名片段>|<被測類別名片段>|<建議排序號方法名>' -r "governance/review-reports/Android單元測試標準實機演練" | cut -c1-200
```
輸出(只列位置與類別,不貼原文):

| 檔 | 行 | 命中 | 屬於 |
|---|---|---|---|
| `r1-邊界-sonnet.md` | 41 | 1 處 | 套件名片段 |
| `r1-整合-sonnet.md` | 14 | 1 處 | 方法名 |
| `r1-整合-sonnet.md` | 68 | 1 處 | 方法名 |
| `r1-整合-sonnet.md` | 92 | 1 處 | 類別名(由被測類別衍生的測試類別) |
| `r1-snapshot.md` | 38 | 1 處 | 類別名 |
| `r1-snapshot.md` | 82 | 1 處 | 套件名(完整 applicationId,含 `dev` 變體尾碼) |

- **緩解**:同一個真實套件名在 3383ff253 就已出現在 7 個已追蹤檔,例如某份既有審查卷證裡的一行工具函式 import。這次是再增加一處。
- **規則依據**:file: `ONBOARDING.md:136` 寫著「此 repo 公開:推東西前確認**無公司識別資訊**(專案名/表名/業務規則)」。
- **建議**:至少把套件名、類別名(含由它衍生的測試類別名)、方法名換成代稱。若決定照原樣保留,要在驗證紀錄補上「含真實 applicationId」,而不是只寫類別名與方法名。

### 2. `bad-tests.kt.txt` 的 B7 預期值是考場實作那一行的改名版
severity: minor
blocking: 否

引句:「val expected = ((rows.mapNotNull { it.seq.toIntOrNull() }.maxOrNull() ?: 0) + 10).toString()」

- 這行就是考場 ViewModel 裡「建議排序號」方法的表達式,只改了名。
- file: `<考場>/…ViewModel 實作檔:88-89`
- 這行的規則已在 `requirements.md` 的 Q3 公開(最大值加 10)。
- 使用者也明確把 `bad-tests.kt.txt` 列為可公開的去識別化原文,所以我只給 minor。
- 但裁定寫的是「不放考場原始碼」,請確認這一行算不算。
- 同檔的 `RecordingSource` 三個方法簽名和 `requirements.md` 的介面區塊,是考場資料來源介面的逐行改名,同樣屬於這個裁量。

### 3. `controls.json` 的歸因樣本沒標明是修補前的狀態
severity: minor
blocking: 否

引句:「"org.junit.ComparisonFailure: expected:<[1]0> but was:<[]0>",」

- `device_attribution_samples` 六筆的 `type_attr` 全是 `null`,包括 `stringEquals`、`bareTrue`、`messageTrue`、`intEquals`。
- 驗證紀錄說這四種「現在收得到證」。對照 file: `scripts/test_quality.py:135`,現行規則會認出這四筆(第一行是 `java.lang.AssertionError` 或 `org.junit.ComparisonFailure`,且有 `org.junit.Assert` 堆疊)。
- 所以這份樣本是修補前才抓的,檔裡沒有任何標註。讀的人會誤以為修補後這四種仍然歸因失敗。
- 建議在 README 或 `controls.json` 補一句「修補前的解析結果」。

### 4. 帳內 exclusions 文字被截掉一段
severity: minor
blocking: 否

引句:「演練分支不推不併;平板只裝  套件,可解除安裝。」

- 「只裝」與「套件」之間是兩個空格,原本應該是一個被反引號包住的套件名,在 shell 展開時被吃掉了。
- 這是 canary 第 17 行,governance-log 第 40 行也有同一句。
- 這不是洩漏,是句意缺字。帳只能追加,所以最多在驗證紀錄註明,不要去改帳。
- 反引號被 shell 執行,也是記憶裡 `heredoc-backticks-execute` 那條已知的坑。

## 去識別化改壞意思(鏡頭 5)
README、`requirements.md`、JSON 之間沒發現矛盾。`name`、`kind`、`seq` 的代稱沒有誤換到一般英文字。`Q3` 的「只有 `-5` 時回 `5`」與 `nextSeq_onlyMinusFive_returnsFive` 一致。README 對 M2 的描述(起點 0 改 -10,結果回 `0`)與 `nextSeq_emptyList` 和 `nextSeq_noIntegerSeqAtAll` 翻紅相符。唯一的語意問題是上面的 finding 3。

總結:最嚴重等級 major,blocking 1 條
