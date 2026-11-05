// 語意覆核級已知誤報:Map.Entry.value、Lazy.value 不是狀態容器,形狀分不出
fun group(map: Map<String, MutableList<Item>>) {
    for (e in map.entries) { e.value.add(Item()) }
    map.entries.forEach { it.value.add(Item()) }
}
fun lazyList() { val lz = lazy { mutableListOf<Int>() }; lz.value.add(1) }
