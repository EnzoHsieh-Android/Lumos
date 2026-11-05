package good

@Composable
fun Editor(initial: String, user: User) {
    var text by remember(initial) { mutableStateOf(initial) }
    var on by remember { mutableStateOf(false) }
    var q by rememberSaveable { mutableStateOf("") }
    var c by remember { mutableStateOf(Color.Red) }
    var m by remember { mutableStateOf(MAX_COUNT) }
}

class Holder(initial: String) {
    val s = remember { mutableStateOf(initial) }
}
