package bad

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
