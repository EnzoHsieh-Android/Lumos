package bad

@Composable
fun Banner(anim: Animatable<Float, *>) {
    Button(onClick = { GlobalScope.launch { anim.animateTo(1f) } }) { } // BAD
    val s = CoroutineScope(Dispatchers.Main) // BAD
    LaunchedEffect(Unit) { MainScope().launch { } } // BAD
}
