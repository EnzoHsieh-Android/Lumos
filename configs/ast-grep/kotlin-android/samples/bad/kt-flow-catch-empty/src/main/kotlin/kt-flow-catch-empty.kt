fun a() {
    flow.catch { }.collect { show(it) } // BAD
    repo.stream().catch { e -> }.launchIn(scope) // BAD
    // BAD-NEXT
    repo.stream()
        .catch { /* 忽略 */ }
        .collect()
}
