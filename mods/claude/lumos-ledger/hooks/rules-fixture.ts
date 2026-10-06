// 外掛與 Python 讀取端共用的規則案例(代碼審:兩種語言各寫一份同一條規則,沒有守衛就會漂移)。
// ledger.test.ts 匯入它跑外掛這邊;scripts/test_lumos.py 的 t_ledger_rules_match_reader 讀這支檔、
// 解析 RULES = 後面那段 JSON,拿同一批案例跑 _EVENTS_SESSION_RE、_vault_in、_events_root。
// ★RULES 後面必須是純 JSON(雙引號、沒有尾逗號、沒有註解)★,Python 那邊用 json.loads 讀。
export const RULES = {
  "session": {
    "ok": ["3917d762-6413-48c4-ae39-1e5e9eea0733", "S1", "a.b_c-d", "0abc"],
    "bad": ["", "../x", ".hidden", "a/b", "-lead", "_lead", "a b", "x\n", "été"]
  },
  "vault": [
    { "dirs": ["docs/demo-knowledge"], "want": true },
    { "dirs": ["docs/knowledge"], "want": true },
    { "dirs": ["MOC", "Systems"], "want": true },
    { "dirs": ["MOC", "Verification"], "want": true },
    { "dirs": ["MOC"], "want": false },
    { "dirs": ["Systems", "Verification"], "want": false },
    { "dirs": ["docs/notes"], "want": false },
    { "dirs": [], "want": false },
    { "dirs": ["docs/real-knowledge-target"], "links": { "docs/demo-knowledge": "docs/real-knowledge-target" }, "want": true }
  ],
  "main": [
    { "top": "/r", "common": "/r/.git", "want": "/r" },
    { "top": "/wt/x", "common": "/r/.git", "want": "/r" },
    { "top": "/r", "common": "/srv/bare.git", "want": "/r" }
  ]
}
