package bad

@Composable
fun Editor(initial: String, user: User) {
    var text by remember { mutableStateOf(initial) } // BAD
    var name by rememberSaveable { mutableStateOf(user.name) } // BAD
    var n by remember { mutableIntStateOf(count) } // BAD
}
