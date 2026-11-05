package good

@Composable
fun Banner(anim: Animatable<Float, *>) {
    val scope = rememberCoroutineScope()
    Button(onClick = { scope.launch { anim.animateTo(1f) } }) { }
    LaunchedEffect(anim) { anim.animateTo(0f) }
}

class AppInit {
    val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)
    fun warm() = scope.launch { }
}
