// 語意覆核級已知誤報:Map.Entry.value 底下的集合
fun fill(map: Map<String, Group>) { map.entries.forEach { it.value.items.add(Item()) } }
