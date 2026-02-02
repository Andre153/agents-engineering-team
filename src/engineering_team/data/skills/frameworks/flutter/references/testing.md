# Flutter Testing Patterns

## Table of Contents
1. [Test Setup](#test-setup)
2. [Unit Tests](#unit-tests)
3. [Cubit/BLoC Tests](#cubitbloc-tests)
4. [Widget Tests](#widget-tests)
5. [Integration Tests](#integration-tests)
6. [Mocking](#mocking)
7. [Golden Tests](#golden-tests)
8. [Best Practices](#best-practices)

---

## Test Setup

### Dependencies

```yaml
dev_dependencies:
  flutter_test:
    sdk: flutter
  bloc_test: ^9.1.5
  mocktail: ^1.0.1
```

### Directory Structure

```
test/
├── features/
│   └── auth/
│       ├── data/
│       │   └── auth_repository_test.dart
│       ├── domain/
│       │   └── login_use_case_test.dart
│       └── presentation/
│           ├── cubit/
│           │   └── login_cubit_test.dart
│           └── pages/
│               └── login_page_test.dart
├── helpers/
│   ├── pump_app.dart
│   └── mocks.dart
└── fixtures/
    └── user.json
```

### Test Helpers

```dart
// test/helpers/pump_app.dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

extension PumpApp on WidgetTester {
  Future<void> pumpApp(
    Widget widget, {
    List<BlocProvider>? providers,
  }) {
    return pumpWidget(
      MaterialApp(
        home: providers != null
            ? MultiBlocProvider(
                providers: providers,
                child: widget,
              )
            : widget,
      ),
    );
  }

  Future<void> pumpRoute(
    Widget widget, {
    List<BlocProvider>? providers,
  }) {
    return pumpWidget(
      MaterialApp(
        home: Scaffold(body: widget),
      ),
    );
  }
}
```

---

## Unit Tests

### Basic Unit Test

```dart
import 'package:test/test.dart';

void main() {
  group('User', () {
    test('creates valid user from json', () {
      final json = {
        'id': '1',
        'name': 'John',
        'email': 'john@example.com',
      };

      final user = User.fromJson(json);

      expect(user.id, equals('1'));
      expect(user.name, equals('John'));
      expect(user.email, equals('john@example.com'));
    });

    test('throws when json is invalid', () {
      final json = {'id': '1'};

      expect(
        () => User.fromJson(json),
        throwsA(isA<FormatException>()),
      );
    });
  });
}
```

### Repository Test

```dart
import 'package:mocktail/mocktail.dart';
import 'package:test/test.dart';

class MockApiClient extends Mock implements ApiClient {}

void main() {
  late UserRepository repository;
  late MockApiClient mockApiClient;

  setUp(() {
    mockApiClient = MockApiClient();
    repository = UserRepository(mockApiClient);
  });

  group('getUser', () {
    const userId = '123';
    final userJson = {'id': userId, 'name': 'John'};

    test('returns user when API call succeeds', () async {
      when(() => mockApiClient.get('/users/$userId'))
          .thenAnswer((_) async => userJson);

      final result = await repository.getUser(userId);

      expect(result.id, equals(userId));
      verify(() => mockApiClient.get('/users/$userId')).called(1);
    });

    test('throws when API call fails', () async {
      when(() => mockApiClient.get('/users/$userId'))
          .thenThrow(NetworkException());

      expect(
        () => repository.getUser(userId),
        throwsA(isA<NetworkException>()),
      );
    });
  });
}
```

---

## Cubit/BLoC Tests

### Cubit Test with bloc_test

```dart
import 'package:bloc_test/bloc_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:test/test.dart';

class MockUserRepository extends Mock implements UserRepository {}

void main() {
  late MockUserRepository mockRepository;

  setUp(() {
    mockRepository = MockUserRepository();
  });

  group('UserCubit', () {
    test('initial state is UserState.initial', () {
      final cubit = UserCubit(mockRepository);
      expect(cubit.state, equals(const UserState()));
    });

    blocTest<UserCubit, UserState>(
      'emits [loading, success] when loadUser succeeds',
      setUp: () {
        when(() => mockRepository.getUser(any()))
            .thenAnswer((_) async => User(id: '1', name: 'John'));
      },
      build: () => UserCubit(mockRepository),
      act: (cubit) => cubit.loadUser('1'),
      expect: () => [
        const UserState(status: UserStatus.loading),
        isA<UserState>()
            .having((s) => s.status, 'status', UserStatus.success)
            .having((s) => s.user?.name, 'user name', 'John'),
      ],
      verify: (_) {
        verify(() => mockRepository.getUser('1')).called(1);
      },
    );

    blocTest<UserCubit, UserState>(
      'emits [loading, failure] when loadUser fails',
      setUp: () {
        when(() => mockRepository.getUser(any()))
            .thenThrow(Exception('Failed'));
      },
      build: () => UserCubit(mockRepository),
      act: (cubit) => cubit.loadUser('1'),
      expect: () => [
        const UserState(status: UserStatus.loading),
        isA<UserState>()
            .having((s) => s.status, 'status', UserStatus.failure)
            .having((s) => s.errorMessage, 'error', isNotNull),
      ],
    );
  });
}
```

### Testing State Changes

```dart
blocTest<CounterCubit, int>(
  'increment increases state by 1',
  build: () => CounterCubit(),
  act: (cubit) => cubit.increment(),
  expect: () => [1],
);

blocTest<CounterCubit, int>(
  'multiple increments work correctly',
  build: () => CounterCubit(),
  act: (cubit) {
    cubit.increment();
    cubit.increment();
    cubit.increment();
  },
  expect: () => [1, 2, 3],
);

blocTest<CounterCubit, int>(
  'increment from seeded state',
  build: () => CounterCubit(),
  seed: () => 10,
  act: (cubit) => cubit.increment(),
  expect: () => [11],
);
```

---

## Widget Tests

### Basic Widget Test

```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/pump_app.dart';

void main() {
  group('CounterWidget', () {
    testWidgets('displays initial count', (tester) async {
      await tester.pumpApp(const CounterWidget(initialCount: 5));

      expect(find.text('5'), findsOneWidget);
    });

    testWidgets('increments count on button tap', (tester) async {
      await tester.pumpApp(const CounterWidget());

      expect(find.text('0'), findsOneWidget);

      await tester.tap(find.byIcon(Icons.add));
      await tester.pump();

      expect(find.text('1'), findsOneWidget);
    });
  });
}
```

### Testing with BLoC

```dart
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

class MockCounterCubit extends MockCubit<int> implements CounterCubit {}

void main() {
  late MockCounterCubit mockCubit;

  setUp(() {
    mockCubit = MockCounterCubit();
  });

  testWidgets('renders count from cubit', (tester) async {
    when(() => mockCubit.state).thenReturn(42);

    await tester.pumpWidget(
      MaterialApp(
        home: BlocProvider<CounterCubit>.value(
          value: mockCubit,
          child: const CounterPage(),
        ),
      ),
    );

    expect(find.text('42'), findsOneWidget);
  });

  testWidgets('calls increment on FAB tap', (tester) async {
    when(() => mockCubit.state).thenReturn(0);

    await tester.pumpWidget(
      MaterialApp(
        home: BlocProvider<CounterCubit>.value(
          value: mockCubit,
          child: const CounterPage(),
        ),
      ),
    );

    await tester.tap(find.byType(FloatingActionButton));

    verify(() => mockCubit.increment()).called(1);
  });
}
```

### Finding Widgets

```dart
// By type
find.byType(ElevatedButton)
find.byType(TextField)

// By text
find.text('Submit')
find.textContaining('Welcome')

// By key
find.byKey(const Key('submit_button'))

// By icon
find.byIcon(Icons.add)

// By widget predicate
find.byWidgetPredicate(
  (widget) => widget is Text && widget.data?.contains('Error') == true,
)

// Descendants
find.descendant(
  of: find.byType(Card),
  matching: find.text('Title'),
)

// Multiple results
expect(find.byType(ListTile), findsNWidgets(3));
expect(find.byType(Divider), findsAtLeastNWidgets(2));
```

### Async Widget Tests

```dart
testWidgets('shows loading then data', (tester) async {
  when(() => mockCubit.state).thenReturn(const UserState(status: UserStatus.loading));

  await tester.pumpWidget(/* ... */);

  expect(find.byType(CircularProgressIndicator), findsOneWidget);

  // Simulate state change
  when(() => mockCubit.state).thenReturn(
    UserState(status: UserStatus.success, user: User(name: 'John')),
  );

  // Rebuild with new state
  await tester.pump();

  expect(find.byType(CircularProgressIndicator), findsNothing);
  expect(find.text('John'), findsOneWidget);
});
```

---

## Integration Tests

### Setup

```yaml
# pubspec.yaml
dev_dependencies:
  integration_test:
    sdk: flutter
```

```dart
// integration_test/app_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:my_app/main.dart' as app;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('complete user flow', (tester) async {
    app.main();
    await tester.pumpAndSettle();

    // Login
    await tester.enterText(find.byKey(const Key('email_field')), 'test@test.com');
    await tester.enterText(find.byKey(const Key('password_field')), 'password');
    await tester.tap(find.byKey(const Key('login_button')));
    await tester.pumpAndSettle();

    // Verify home screen
    expect(find.text('Welcome'), findsOneWidget);

    // Navigate to profile
    await tester.tap(find.byIcon(Icons.person));
    await tester.pumpAndSettle();

    expect(find.text('Profile'), findsOneWidget);
  });
}
```

### Running Integration Tests

```bash
# Run on connected device
flutter test integration_test/app_test.dart

# Run on specific device
flutter test integration_test/app_test.dart -d <device_id>
```

---

## Mocking

### With Mocktail

```dart
import 'package:mocktail/mocktail.dart';

// Mock class
class MockUserRepository extends Mock implements UserRepository {}

// Register fallback values for custom types
setUpAll(() {
  registerFallbackValue(User(id: '', name: '', email: ''));
});

// Stub methods
when(() => mockRepo.getUser(any())).thenAnswer((_) async => user);
when(() => mockRepo.saveUser(any())).thenAnswer((_) async {});
when(() => mockRepo.deleteUser(any())).thenThrow(Exception('Failed'));

// Verify calls
verify(() => mockRepo.getUser('123')).called(1);
verifyNever(() => mockRepo.deleteUser(any()));
```

### Mock Cubit

```dart
import 'package:bloc_test/bloc_test.dart';

class MockAuthCubit extends MockCubit<AuthState> implements AuthCubit {}

void main() {
  late MockAuthCubit mockAuthCubit;

  setUp(() {
    mockAuthCubit = MockAuthCubit();
  });

  // Stub state
  when(() => mockAuthCubit.state).thenReturn(AuthAuthenticated(user));

  // Stub stream for BlocListener tests
  whenListen(
    mockAuthCubit,
    Stream.fromIterable([AuthLoading(), AuthAuthenticated(user)]),
    initialState: AuthInitial(),
  );
}
```

---

## Golden Tests

### Basic Golden Test

```dart
testWidgets('MyWidget matches golden', (tester) async {
  await tester.pumpWidget(
    MaterialApp(
      home: MyWidget(),
    ),
  );

  await expectLater(
    find.byType(MyWidget),
    matchesGoldenFile('goldens/my_widget.png'),
  );
});
```

### Update Goldens

```bash
flutter test --update-goldens
```

---

## Best Practices

### Test Organization

```dart
void main() {
  // Group related tests
  group('UserCubit', () {
    // Setup shared dependencies
    late MockUserRepository mockRepository;

    setUp(() {
      mockRepository = MockUserRepository();
    });

    // Nested groups for methods
    group('loadUser', () {
      test('success case', () { /* ... */ });
      test('failure case', () { /* ... */ });
    });

    group('updateUser', () {
      test('success case', () { /* ... */ });
    });
  });
}
```

### Naming Conventions

```dart
// Unit tests: describe what it does
test('returns user when API call succeeds', () {});
test('throws NetworkException when offline', () {});

// Widget tests: describe user interaction
testWidgets('shows error message when login fails', (tester) async {});
testWidgets('navigates to home after successful login', (tester) async {});

// BLoC tests: describe state transitions
blocTest<UserCubit, UserState>(
  'emits [loading, success] when loadUser succeeds',
);
```

### What to Test

| Layer | What to Test |
|-------|--------------|
| Domain | Business logic, validation rules, entity behavior |
| Data | Repository methods, data transformations, error handling |
| Cubit/BLoC | State transitions, side effects, error states |
| Widget | User interactions, conditional rendering, callbacks |
| Integration | Critical user flows end-to-end |

### What NOT to Test

- Flutter framework code (e.g., built-in widgets work)
- Third-party packages (trust their tests)
- Simple getters/setters with no logic
- Generated code
