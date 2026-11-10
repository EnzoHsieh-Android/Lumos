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

// 容易誤報:Service 不是畫面。官方說 repeatOnLifecycle 是為了「只在 UI 顯示在畫面上時處理」,
// Service 本來就要在背景收(LifecycleService 與它的子類別 MediaSessionService、MediaLibraryService)
class SyncService : LifecycleService() {
    override fun onCreate() {
        super.onCreate()
        lifecycleScope.launch { repo.changes.collect { upload(it) } } // GOOD
        lifecycleScope.launch(Dispatchers.IO) { repo.events.collect { save(it) } } // GOOD
        repo.pings.onEach { log(it) }.launchIn(lifecycleScope) // GOOD
    }
}

class PlaybackService : androidx.media3.session.MediaSessionService() {
    override fun onCreate() {
        super.onCreate()
        lifecycleScope.launch { player.events.collectLatest { update(it) } } // GOOD
    }
}
