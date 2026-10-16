import Foundation

actor SearchStore {
    private(set) var result = ""

    func load(_ value: String, delay: UInt64) async {
        try? await Task.sleep(nanoseconds: delay)
        result = value
    }
}

@main struct Main {
    static func main() async {
        let store = SearchStore()
        if CommandLine.arguments.last == "normal" {
            await store.load("old", delay: 1_000_000)
            await store.load("new", delay: 1_000_000)
            exit(await store.result == "new" ? 0 : 3)
        }
        async let old: Void = store.load("old", delay: 80_000_000)
        try? await Task.sleep(nanoseconds: 5_000_000)
        async let new: Void = store.load("new", delay: 5_000_000)
        _ = await (old, new)
        exit(await store.result == "new" ? 0 : 1)
    }
}
