class ProfileFragment : Fragment() {
    override fun onViewCreated(view: View, state: Bundle?) {
        vm.user.observe(viewLifecycleOwner) { render(it) } // GOOD
        vm.items.observe(viewLifecycleOwner, Observer { show(it) }) // GOOD
    }
}

// 容易誤報:Activity 裡 observe(this) 是對的,Activity 沒有獨立的畫面生命週期
class MainActivity : AppCompatActivity() {
    override fun onCreate(state: Bundle?) {
        super.onCreate(state)
        vm.user.observe(this) { render(it) } // GOOD
    }
}
