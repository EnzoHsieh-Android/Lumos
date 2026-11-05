package good

class FeedFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                vm.state.collect { render(it) }
            }
        }
        lifecycleScope.launch {
            vm.events.flowWithLifecycle(lifecycle).collect { show(it) }
        }
        lifecycleScope.launch {
            val first = vm.config.first()
        }
        vm.toasts.flowWithLifecycle(lifecycle).onEach { toast(it) }.launchIn(lifecycleScope)
    }
}

// 容易誤報:Compose 用 collectAsStateWithLifecycle,沒有 lifecycleScope.launch
@Composable
fun FeedScreen(vm: FeedViewModel) {
    val state by vm.state.collectAsStateWithLifecycle() // GOOD
    Feed(state)
}
