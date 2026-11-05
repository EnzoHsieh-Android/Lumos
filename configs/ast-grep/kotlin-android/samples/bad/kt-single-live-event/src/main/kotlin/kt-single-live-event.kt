package bad

// case: subclass-mutablelivedata
class SingleLiveEvent<T> : MutableLiveData<T>() {
    private val pending = AtomicBoolean(false)
}
// case: getContentIfNotHandled
fun Fragment.bind(vm: VM) {
    vm.navigate.observe(viewLifecycleOwner) { event ->
        event.getContentIfNotHandled()?.let { findNavController().navigate(it) }
    }
}
// case: safe-call-getContent
fun handle(e: Event<String>?) { e?.getContentIfNotHandled() }
// case: named-live-event
class LiveEvent<T> : MediatorLiveData<T>()
