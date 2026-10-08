// 審查席標記的共用案例(Projects/事件帳補記搜尋與席位_計劃 S3、S4):事件帳外掛的 seatOf 與審查席隔離外掛的 parseMarker
// 各寫一份;這份案例兩支外掛各放一份一模一樣的(t_ledger_seat_re_matches_guard 比對兩份),兩邊的測試都跑——seat 是守衛判成審查席時的「迴圈/輪次/席名」,其他(不是標記、寫壞)都是 null。
export const SEAT_CASES: readonly { prompt: string; seat: string | null }[] = [
  { prompt: 'LUMOS-SEAT: 迴圈/r1/正確性-sonnet\n請審查', seat: '迴圈/r1/正確性-sonnet' },
  { prompt: '\n  LUMOS-SEAT: a/r1/b', seat: 'a/r1/b' },
  { prompt: '\r\nLUMOS-SEAT: a/r1/b\r\n內文', seat: 'a/r1/b' },
  { prompt: '​\nLUMOS-SEAT: a/r1/b', seat: 'a/r1/b' },
  { prompt: '­\nLUMOS-SEAT: a/r1/b', seat: 'a/r1/b' },
  { prompt: 'LUMOS-SEAT: a/r1/b 請審查', seat: 'a/r1/b' },
  { prompt: ' LUMOS-SEAT: a/r1/b', seat: 'a/r1/b' },
  { prompt: 'LUMOS-SEAT: a/r3-dref/b', seat: 'a/r3-dref/b' },
  { prompt: 'LUMOS-SEAT: a/b', seat: null },
  { prompt: 'LUMOS-SEAT: a/r1/b/c', seat: null },
  { prompt: 'LUMOS-SEAT: a/../b', seat: null },
  { prompt: 'LUMOS-SEAT: a//b', seat: null },
  { prompt: 'LUMOS-SEAT: a/r1/b​', seat: null },
  { prompt: 'LUMOS-SEAT：a/r1/b', seat: null },
  { prompt: 'lumos-seat: a/r1/b', seat: null },
  { prompt: '說明\nLUMOS-SEAT: a/r1/b', seat: null },
  { prompt: 'LUMOS-SEAT: a b', seat: null },
  { prompt: '請審查', seat: null },
  { prompt: '', seat: null },
]
