package bad

// case: fragment-collect(畫面類別裡三種收集寫法都報)
class FeedFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewLifecycleOwner.lifecycleScope.launch {
            vm.state.collect { render(it) } // BAD
        }
        lifecycleScope.launch {
            vm.events.collectLatest { show(it) } // BAD
        }
        vm.toasts.onEach { toast(it) }.launchIn(lifecycleScope) // BAD
    }
}

// case: service-listener(實作 MediaSessionService.Listener 不是 Service 建構子呼叫,照報)
class PlayerFragment : Fragment(), MediaSessionService.Listener {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        lifecycleScope.launch { vm.player.collect { draw(it) } } // BAD
    }
}

// case: process-lifecycle-owner(非 Service 類別裡照報:官方說它是所有 Activity 的合成生命週期)
class BannerFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        ProcessLifecycleOwner.get().lifecycleScope.launch { session.state.collect { show(it) } } // BAD
    }
}

// case: activity-own-collect(例外只看類別自己的繼承清單,Activity 自己的收集照報)
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycleScope.launch { vm.state.collect { render(it) } } // BAD
    }
}
