class F : Fragment() {
    fun onSave(x: Item) {
        lifecycleScope.launch { repository.save(x) } // BAD
        viewLifecycleOwner.lifecycleScope.launch(Dispatchers.IO) { userDao.insert(x) } // BAD
    }
}
