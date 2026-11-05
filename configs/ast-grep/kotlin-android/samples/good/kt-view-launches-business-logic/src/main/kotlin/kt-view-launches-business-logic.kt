class F : Fragment() {
    fun onSave(x: Item) {
        viewModel.save(x) // GOOD
        lifecycleScope.launch { viewModel.submit(x) } // GOOD
        viewLifecycleOwner.lifecycleScope.launch { // GOOD
            repeatOnLifecycle(Lifecycle.State.STARTED) { viewModel.ui.collect { render(it) } }
        }
    }
}

// 容易誤報:lifecycleScope 只做畫面上的事(顯示 snackbar),業務工作交給 viewModel
class SettingsActivity : AppCompatActivity() {
    fun onSave() {
        viewModel.save() // GOOD
        lifecycleScope.launch { snackbarHost.showSnackbar("saved") } // GOOD
    }
}
