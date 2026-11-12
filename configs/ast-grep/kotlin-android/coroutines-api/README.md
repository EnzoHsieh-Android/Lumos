# coroutines-api

型錄〈API 決策點〉的母體:kotlinx-coroutines-core 1.10.2 的官方公開 API 清單,逐位元組照抄,不准手改(型錄第一行記兩份的 sha256,自檢 `check.py` 的 `api_decision_problems` 會核對)。

| 檔 | 來源 |
|---|---|
| `kotlinx-coroutines-core-1.10.2.klib.api` | https://github.com/Kotlin/kotlinx.coroutines/blob/1.10.2/kotlinx-coroutines-core/api/kotlinx-coroutines-core.klib.api |
| `kotlinx-coroutines-core-1.10.2.api` | https://github.com/Kotlin/kotlinx.coroutines/blob/1.10.2/kotlinx-coroutines-core/api/kotlinx-coroutines-core.api |
| `jvm-only.txt` | 本 repo 手列:JVM 專屬、klib 清單沒有的公開名稱(檔頭寫了初版怎麼判) |

兩份 `.api` 檔由 kotlinx.coroutines 專案以 Apache License 2.0 釋出(https://github.com/Kotlin/kotlinx.coroutines/blob/1.10.2/LICENSE.txt ,授權檔原文:「Copyright 2000-2020 JetBrains s.r.o. and Kotlin Programming Language contributors.」;該版沒有 NOTICE 檔)。這裡只當比對用的資料,沒有修改。

換版本:兩份一起換成新標籤的原檔,改型錄〈API 決策點〉第一行的版本、網址與 sha256,跑 `python3 configs/ast-grep/kotlin-android/check.py --catalog-only`,把新多出來的名稱逐一分類;`jvm-only.txt` 照檔頭的判法重判一次。設計與判準見 `docs/lumos-toolchain-knowledge/Projects/情境決策點窮舉與壞寫法要叫得出_計劃.md`。
