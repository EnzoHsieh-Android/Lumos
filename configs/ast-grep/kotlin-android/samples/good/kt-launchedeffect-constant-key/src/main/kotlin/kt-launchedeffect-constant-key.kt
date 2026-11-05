@Composable
fun Screen(id: String, onDone: () -> Unit) {
    val current by rememberUpdatedState(onDone)
    LaunchedEffect(id) { load(id) } // GOOD
    LaunchedEffect(Unit) { current() } // GOOD
    LaunchedEffect(Unit) { analytics.screen.id.let { log(it) } } // GOOD
}

// 容易誤報(代碼審 r1 M6):參數是不會換的狀態容器或 ViewModel;具名引數的標籤不是參數
@Composable
fun Holders(snackbarHostState: SnackbarHostState, viewModel: HomeViewModel, listState: LazyListState) {
    LaunchedEffect(Unit) { snackbarHostState.showSnackbar("x") }
    LaunchedEffect(Unit) { viewModel.events.collect { } }
    LaunchedEffect(Unit) { listState.scrollToItem(0) }
}

@Composable
fun Labels(vm: HomeViewModel, id: Int) {
    LaunchedEffect(id) { }
    LaunchedEffect(Unit) { vm.load(id = 5) }
}
