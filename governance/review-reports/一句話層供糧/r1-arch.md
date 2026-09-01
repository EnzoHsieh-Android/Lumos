## 一句話層供糧_計劃(l0-r1)對照結果(架構對齊席,sonnet,不佔數)

**A-1**|minor|blocking:否
引句:「每行「名 [status] 決策 N 條」之後加「— <L0>」(空則不加)」(材料 T2)
對照 scripts/lumos:6221-6224(現況已有 ★近名 尾碼)。spec 沒定「— L0」與既有 ★近名 兩個尾碼同時出現時的排列順序(接哪個在前);兩處清單本身(入口栓 A 用 - name [status] 決策N條、cmd_context 鄰居用 • name [status],見 scripts/lumos:7444)格式本就不同屬既存事實而非本案引入,新尾碼借用的是 cmd_context 既有的「— hint」慣例(同一慣例、非另立第二種)。

**A-2**|minor|blocking:否
引句:「L0 取層函式(單一實作)」(材料 T1 標題)
對照候選落點 scripts/lumos:308(first_line)、scripts/lumos:5300(_esc_clean)、scripts/lumos:5979(_el_related_nodes)——spec 沒釘 _gist 該落在哪個函式群附近,是設計階段常見留白,不算違反入口栓 d1 教訓(該教訓管的是「復用要指名」,spec 已指名 first_line/_esc_clean)。

**一致面**(核對過、與既有做法相符,不列為 finding):
- _esc_clean(v, limit=200) 的 limit 參數天生相容截 80,且 80 已有先例:scripts/lumos:5356 就是 _esc_clean(r['defect_ref'], 80)。
- cmd_context 的鄰居 hint(scripts/lumos:7442-7444)本身就是呼叫共用函式 first_line(),不是行內邏輯;spec 在 PRIOR-ART 與 T1 步驟 2 已明確指名復用,滿足入口栓 d1「spec 階段就指名」的教訓。
- JSON 加 gist 鍵對齊 EL-16「逐欄寫死型別」慣例(docs/lumos-toolchain-knowledge/Projects/圖譜進迴圈入口栓_計劃.md:93;程式碼合約在 scripts/lumos:5984)。
- context --brief 現況確實丟鄰居 hint(scripts/lumos:7436-7444,brief 分支直接 continue 略過 hint 賦值),spec 描述屬實,一行修法方向合理。
- T3 落點逐字精確命中 skills/lumos-code-loop/SKILL.md:19(「超出上限的列名即可,不必答」逐字存在),引用的 d9 決策逐字對應 docs/lumos-toolchain-knowledge/Systems/design-loop.md:113(decided: 2026-09-01)。
- 機械數複核:白話行 84 篇(grep -rl 復核=84,精確)、Systems 4/58(精確);全篇數材料寫 389、本次復核 390(帳是活的,材料已自行聲明,不算落差)。

severity: minor
