package bad

@Composable
fun R1() {
    Row(Modifier.clickable { open() }) { Text("a") } // BAD
    Box(Modifier.padding(4.dp).clickable(enabled = true) { open() }) // BAD
    Card(Modifier.clickable(onClick = { open() })) { } // BAD
}
