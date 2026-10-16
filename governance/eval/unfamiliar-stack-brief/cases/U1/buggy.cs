sealed class ScopedResource : IDisposable
{
    private bool _disposed;
    public int Read() => _disposed ? throw new ObjectDisposedException(nameof(ScopedResource)) : 42;
    public void Dispose() => _disposed = true;
}

static class Program
{
    static int Main(string[] args)
    {
        if (args.SingleOrDefault() == "normal")
        {
            using var live = new ScopedResource();
            return live.Read() == 42 ? 0 : 3;
        }

        var requestResource = new ScopedResource();
        Func<int> queuedWork = () => requestResource.Read();
        requestResource.Dispose();
        try
        {
            queuedWork();
            return 2;
        }
        catch (ObjectDisposedException)
        {
            return 1;
        }
    }
}
