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
// case: oneshot-unpeek(代碼審 r2 規則B Finding 11:事件包裝的其他常見名)
class OneShotLiveData<T> : MutableLiveData<T>()
class UnPeekLiveData<T> : MutableLiveData<T>()
