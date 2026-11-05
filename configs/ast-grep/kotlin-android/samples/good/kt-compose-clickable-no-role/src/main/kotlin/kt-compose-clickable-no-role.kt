package good

@Composable
fun R1() {
    Row(Modifier.clickable(role = Role.Button) { open() }) { Text("a") }
    Box(Modifier.clickable(onClickLabel = stringResource(R.string.open)) { open() })
    Card(Modifier.combinedClickable(onClick = {}, onLongClick = {}, role = Role.Button)) { }
    Button(onClick = { open() }) { Text("b") }
}
