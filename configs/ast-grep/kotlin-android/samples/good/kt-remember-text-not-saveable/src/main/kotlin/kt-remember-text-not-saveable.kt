@Composable
fun SearchBox() {
    var text by rememberSaveable { mutableStateOf("") } // GOOD
    TextField(value = text, onValueChange = { text = it })
}

@Composable
fun NoteEditor() {
    var value by rememberSaveable(stateSaver = TextFieldValue.Saver) { mutableStateOf(TextFieldValue("")) } // GOOD
    TextField(value = value, onValueChange = { value = it })
}

// 容易誤報:remember 一個不是使用者輸入的暫態(展開與否)
@Composable
fun Section() {
    var expanded by remember { mutableStateOf(false) } // GOOD
    Header(expanded, onToggle = { expanded = !expanded })
}
