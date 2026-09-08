# r1 席位對帳補記(不綁帳,記帳後寫)

`loop status --disposal` 的 [roster] 段印「同門 0 席 / 外家未派 / 單家族」——**是席名沒帶模型尾碼造成的辨識失敗,不是真的沒派**。
實派:通才、接手的人、簡化守護者、架構對齊 = sonnet(Agent);外家否決 = Codex gpt-5.6-terra medium(`codex exec --sandbox read-only`)。
證據:`r1-dispatch.json`(五席名單)、`r1-codex-raw.txt`(Codex 逐字稿含 model 行)、`r1-codex-prompt.txt`。
慣例應寫 `<鏡頭>-<模型>`(如 `外家否決-codex`、`通才-sonnet`),上一案 enforcement可觀測性 r1 同樣漏了(roster-alerts.log 有 seat_shortfall,單家族)。
帳只能加不能改,所以留這一份補記;下一輪起席名照慣例。
