class ProfileFragment : Fragment() {
    override fun onViewCreated(view: View, state: Bundle?) {
        viewLifecycleOwner.lifecycleScope.launchWhenStarted { // BAD
            vm.state.collect { render(it) }
        }
    }
}

class MainActivity : AppCompatActivity() {
    override fun onCreate(state: Bundle?) {
        super.onCreate(state)
        lifecycleScope.launch {
            launchWhenResumed { vm.events.collect { handle(it) } } // BAD
        }
    }
}
