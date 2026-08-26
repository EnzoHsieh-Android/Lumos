### ext-f1
severity: clean
引句:「擋下:--outcome 結局帳只能用 kind=none——kind=caught/missed 掛結局欄可湊 legacy 閘輪次(cb3 r2 delta 活體重現)」
佐證:file: `scripts/lumos:4024`
說明:已解。第一刀會拒絕 kind=caught/missed 搭配 --outcome；第二刀會拒絕 --outcome 與 round、severity、report、snapshot、findings 或 findings-set 任一混用，皆回傳 rc2。另核對了 kind=none+outcome 搭處置欄、folded/accepted/accept-reason/finding-kind、--usd/--note、純 outcome 不帶 auditor，以及漏 round 的審查席：處置組合會被互斥或配套檢查拒絕；usd/note 是合法結局欄；無 auditor 的純 outcome 不具審查席形狀且缺 severity，不能形成乾淨判定輪；loop+auditor 無 outcome 仍強制報告並核對不得低報。未找到其他可跳過整層寫側守衛的旗標組合。補丁雜湊亦吻合指定的 5e0085abfe2d2dff5e42050d237f11c9f5b4fe20b1926fc28f5b97eaa2860045。

結論:否決解除（ext-f1 兩條繞道均已封閉，未發現替代旗標繞法）。
