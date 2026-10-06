// 只給 $.state 用:lumos-guard 放進 $.state 的值,子代理編號 → 審查席(熱重載後還在,外掛讀回來繼續擋;
// session 是所屬會談,會談結束時只刪那一場;/clear 與接續結束的不刪)
export type GuardSeat = { loop: string; round: string; name: string; cwd: string; session?: string }

declare module 'claude-code' {
  interface PluginState {
    'lumos-guard': { seats: Record<string, GuardSeat> }
  }
}
