class ProfileFragment : Fragment() {
    override fun onViewCreated(view: View, state: Bundle?) {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) { // GOOD
                vm.state.collect { render(it) }
            }
        }
    }
}

// 容易誤報:普通的 launch 加 repeatOnLifecycle(RESUMED),名字有 Resumed 但不是 launchWhenResumed
class MainActivity : AppCompatActivity() {
    override fun onCreate(state: Bundle?) {
        super.onCreate(state)
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.RESUMED) { vm.events.collect { handle(it) } } // GOOD
        }
    }
}
