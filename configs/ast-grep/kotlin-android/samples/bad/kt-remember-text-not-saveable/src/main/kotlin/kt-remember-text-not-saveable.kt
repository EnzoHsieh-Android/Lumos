@Composable
fun SearchBox() {
    var text by remember { mutableStateOf("") } // BAD
    TextField(value = text, onValueChange = { text = it })
}

@Composable
fun NoteEditor() {
    var value by remember { mutableStateOf(TextFieldValue("")) } // BAD
    TextField(value = value, onValueChange = { value = it })
}
