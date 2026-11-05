package good

@Composable
fun Contacts(list: List<C>, onPick: (List<C>) -> Unit) {
    val sorted = remember(list) { list.sortedBy { it.name } }
    val adults by remember { derivedStateOf { list.filter { it.age >= 18 } } }
    Button(onClick = { onPick(list.filter { it.age > 1 }) }) { Text("x") }
    LaunchedEffect(list) { cache = list.sortedBy { it.id } }
    LazyColumn { items(sorted, key = { it.id }) { Text(it.name) } }
}

class ContactsVm {
    fun sorted(list: List<C>) = list.sortedBy { it.name }.filter { it.age > 0 }
}
