C1 [❌] 節點實際 frontmatter `type:` 為 `system`,非 `known-pitfall`；「known-pitfall」只是 Systems 節點下的命名/欄位慣例(前綴+pitfall_ask/pitfall_source),非正式 type 值;「與其他 known-pitfall-* 節點共用慣例」亦查無其他實例佐證 | 證據: scripts/lumos:803-819(check-S 迴圈只掃 `n.fields.get("type") == "system"`,known-pitfall-refresh-token 持續被此閘命中→其 type 必為 system)、docs/.governance-log.jsonl:14539(該節點被 check-s 閘命中,佐證其 type=system)、governance/review-reports/已知坑策展庫/r1-snapshot.md:28(「known-pitfall = Systems 節點,frontmatter 三欄」明白將 known-pitfall 定義為命名慣例而非 type 值)、skills/lumos-pitfalls-gapfill/SKILL.md:46(建節點指令為 `lumos new system known-pitfall-<pattern>`,即 type=system)；repo 內未見第二個 known-pitfall-* 具體節點可佐證「共用慣例」

C2 [⏭] 主張自標「外部知識,repo 不可驗」,略過

C3 [✅] content-trigger 正則機制屬實,且該確切正則字串見於落地前設計文件 | 證據: scripts/lumos:11928-11976(`_pitfall_scan_known` 讀 `pitfall_when` 中 `content:` 前綴項,對 spec corpus `re.search`,命中即攤出 advisory)、governance/review-reports/已知坑策展庫/r1-snapshot.md:47(`pitfall_when: ["content:refresh.?token|refreshToken|token.?rotat"]`)

C4 [❓] 找不到 repo 內任何可讀位置提及 Verification 節點「已知坑策展庫v2落地」 | 已搜:governance/(全部 review-reports、eval)、scripts/lumos、scripts/test_lumos.py、skills/、docs/.*.jsonl,均無「已知坑策展庫v2落地」字串命中

C5 [✅] pitfalls 指令對 md 檔(spec 文本)執行 design-time 掃描,命中 content-trigger 即以 advisory 形式印出已知坑提問 | 證據: scripts/lumos:11909-11946(`cmd_pitfalls` 讀 `<md檔>` 文本轉 corpus→`_pitfall_scan_known`→`known` 非空則印「已知坑追問(世界已知,advisory...)」段)

C6 [✅] 處置規範原文與 panel 審機制皆吻合 | 證據: scripts/lumos:11943(`print("已知坑追問(世界已知,advisory——答或寫『已排除:理由』,panel 審):")`)、governance/review-reports/已知坑策展庫/r1-snapshot.md:42(「advisory-only,不進 --check 判定;它的牙齒=design-loop panel 審實務隱患節時,對照有沒有答/排除(v1 裁定留痕紀律)」)

C7 [⏭] 主張自標「外部知識,repo 不可驗」,略過

C8 [⏭] 主張自標「外部知識,repo 不可驗」,略過

C9 [⏭] 主張自標「外部知識,repo 不可驗」,略過

C10 [⏭] 主張自標「外部知識,repo 不可驗」,略過

C11 [✅] created/updated 2026-08-09 與落地時間線一致(design 文件同日 created/updated,且節點首次出現於治理帳同日) | 證據: governance/review-reports/已知坑策展庫/r1-snapshot.md:4-5(`created: 2026-08-09` / `updated: 2026-08-09`,同案設計文件明定當日建 `Systems/known-pitfall-refresh-token.md`)、docs/.governance-log.jsonl:14539(該節點首次出現於 check-s 閘帳,ts=2026-08-09T00:48:29+08:00);查無後續使 `updated` 欄位變動的證據,故僅能佐證創建日,不能排除之後被改

C12 [❓] 無法直接證實 status 標籤確切為 `status/doing`；僅能間接證實其 status 不屬於 stale/superseded | 證據: scripts/lumos:812(check-S 迴圈對 `status` 為 stale/superseded 的節點 `continue` 跳過)、docs/.governance-log.jsonl(known-pitfall-refresh-token 持續被 check-s 閘命中至 2026-08-20,顯示其 status 不在 stale/superseded 之列),但無法機械確認確切值是否為「doing」

✅5 ❌1 ❓2 ⏭4
