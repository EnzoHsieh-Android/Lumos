package bad

@Composable
fun Bar(onClose: () -> Unit) {
    IconButton(onClick = onClose) {
        Icon(Icons.Default.Close, contentDescription = null) // BAD
    }
    FloatingActionButton(onClick = {}) { Icon(Icons.Default.Add, contentDescription = null) } // BAD
    Icon(
        Icons.Default.Share,
        contentDescription = null, // BAD
        modifier = Modifier.clickable { share() },
    )
}
