import 'dart:async';
import 'dart:io';

class Screen {
  int events = 0;
  StreamSubscription<int>? subscription;

  void mount(Stream<int> stream) {
    subscription = stream.listen((_) => events++);
  }

  Future<void> dispose() async {}
}

Future<void> main(List<String> args) async {
  final bus = StreamController<int>.broadcast();
  final screen = Screen()..mount(bus.stream);
  if (args.singleOrNull == 'normal') {
    bus.add(1);
    await Future<void>.delayed(Duration.zero);
    await screen.dispose();
    await bus.close();
    exitCode = screen.events == 1 ? 0 : 3;
    return;
  }
  await screen.dispose();
  bus.add(1);
  await Future<void>.delayed(Duration.zero);
  await bus.close();
  exitCode = screen.events == 0 ? 0 : 1;
}
