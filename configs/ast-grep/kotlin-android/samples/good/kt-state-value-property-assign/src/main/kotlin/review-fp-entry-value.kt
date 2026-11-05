// 語意覆核級已知誤報:Map.Entry.value、自訂 holder 的 .value 不是狀態容器
fun rename(map: Map<String, User>) { for (entry in map.entries) { entry.value.name = "x" } }
fun bump(slider: Holder) { slider.value.foo = 3 }
