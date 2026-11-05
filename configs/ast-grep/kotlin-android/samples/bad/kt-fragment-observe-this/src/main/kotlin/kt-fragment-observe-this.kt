class ProfileFragment : Fragment() {
    override fun onViewCreated(view: View, state: Bundle?) {
        vm.user.observe(this) { render(it) } // BAD
        vm.items.observe(this, Observer { show(it) }) // BAD
    }
}
