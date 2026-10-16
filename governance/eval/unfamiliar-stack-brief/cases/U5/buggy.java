import java.util.ArrayList;
import java.util.List;

public final class TransactionCase {
    static final class Ledger {
        final List<String> rows = new ArrayList<>();
    }

    static final class Service {
        private final Ledger ledger;
        Service(Ledger ledger) { this.ledger = ledger; }
        void place(boolean fail) { writeTwoSteps(fail); }
        void writeTwoSteps(boolean fail) {
            ledger.rows.add("first");
            if (fail) throw new IllegalStateException("second write failed");
            ledger.rows.add("second");
        }
    }

    interface Work { void run(); }
    static void transactional(Ledger ledger, Work work) {
        var before = new ArrayList<>(ledger.rows);
        try { work.run(); }
        catch (RuntimeException error) {
            ledger.rows.clear();
            ledger.rows.addAll(before);
            throw error;
        }
    }

    public static void main(String[] args) {
        var ledger = new Ledger();
        var service = new Service(ledger);
        if (args[0].equals("normal")) {
            transactional(ledger, () -> service.writeTwoSteps(false));
            System.exit(ledger.rows.size() == 2 ? 0 : 3);
        }
        try { service.place(true); } catch (IllegalStateException ignored) {}
        System.exit(ledger.rows.isEmpty() ? 0 : 1);
    }
}
