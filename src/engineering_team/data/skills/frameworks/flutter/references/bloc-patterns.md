# BLoC & Cubit Patterns

## Table of Contents
1. [Cubit Fundamentals](#cubit-fundamentals)
2. [State Design](#state-design)
3. [Async Operations](#async-operations)
4. [BLoC When Needed](#bloc-when-needed)
5. [Testing Cubits](#testing-cubits)
6. [Provider Patterns](#provider-patterns)
7. [Common Patterns](#common-patterns)

---

## Cubit Fundamentals

### Basic Cubit

```dart
import 'package:flutter_bloc/flutter_bloc.dart';

class CounterCubit extends Cubit<int> {
  CounterCubit() : super(0);

  void increment() => emit(state + 1);
  void decrement() => emit(state - 1);
  void reset() => emit(0);
}
```

### Cubit with Complex State

```dart
import 'package:equatable/equatable.dart';

@immutable
class ProfileState extends Equatable {
  final String name;
  final String email;
  final bool isEditing;

  const ProfileState({
    this.name = '',
    this.email = '',
    this.isEditing = false,
  });

  ProfileState copyWith({
    String? name,
    String? email,
    bool? isEditing,
  }) {
    return ProfileState(
      name: name ?? this.name,
      email: email ?? this.email,
      isEditing: isEditing ?? this.isEditing,
    );
  }

  @override
  List<Object?> get props => [name, email, isEditing];
}

class ProfileCubit extends Cubit<ProfileState> {
  ProfileCubit() : super(const ProfileState());

  void updateName(String name) => emit(state.copyWith(name: name));
  void updateEmail(String email) => emit(state.copyWith(email: email));
  void toggleEditing() => emit(state.copyWith(isEditing: !state.isEditing));
}
```

---

## State Design

### Sealed Classes for State Variants (Dart 3+)

```dart
sealed class AuthState extends Equatable {
  const AuthState();
}

class AuthInitial extends AuthState {
  const AuthInitial();
  @override
  List<Object?> get props => [];
}

class AuthLoading extends AuthState {
  const AuthLoading();
  @override
  List<Object?> get props => [];
}

class AuthAuthenticated extends AuthState {
  final User user;
  const AuthAuthenticated(this.user);
  @override
  List<Object?> get props => [user];
}

class AuthUnauthenticated extends AuthState {
  const AuthUnauthenticated();
  @override
  List<Object?> get props => [];
}

class AuthError extends AuthState {
  final String message;
  const AuthError(this.message);
  @override
  List<Object?> get props => [message];
}
```

### Handling Sealed States in UI

```dart
BlocBuilder<AuthCubit, AuthState>(
  builder: (context, state) => switch (state) {
    AuthInitial() => const SizedBox.shrink(),
    AuthLoading() => const CircularProgressIndicator(),
    AuthAuthenticated(:final user) => Text('Hello, ${user.name}'),
    AuthUnauthenticated() => const LoginButton(),
    AuthError(:final message) => Text('Error: $message'),
  },
)
```

### Status Enum Pattern (Alternative)

```dart
enum FormStatus { initial, loading, success, failure }

class FormState extends Equatable {
  final FormStatus status;
  final String name;
  final String? errorMessage;

  const FormState({
    this.status = FormStatus.initial,
    this.name = '',
    this.errorMessage,
  });

  bool get isLoading => status == FormStatus.loading;
  bool get isSuccess => status == FormStatus.success;
  bool get hasError => status == FormStatus.failure;

  FormState copyWith({
    FormStatus? status,
    String? name,
    String? errorMessage,
  }) {
    return FormState(
      status: status ?? this.status,
      name: name ?? this.name,
      errorMessage: errorMessage ?? this.errorMessage,
    );
  }

  @override
  List<Object?> get props => [status, name, errorMessage];
}
```

---

## Async Operations

### Loading States

```dart
class UsersCubit extends Cubit<UsersState> {
  final UserRepository _repository;

  UsersCubit(this._repository) : super(const UsersState());

  Future<void> loadUsers() async {
    emit(state.copyWith(status: UsersStatus.loading));

    try {
      final users = await _repository.getUsers();
      emit(state.copyWith(
        status: UsersStatus.success,
        users: users,
      ));
    } catch (e) {
      emit(state.copyWith(
        status: UsersStatus.failure,
        errorMessage: e.toString(),
      ));
    }
  }
}
```

### Refresh Pattern

```dart
Future<void> refresh() async {
  // Don't show loading indicator on refresh
  try {
    final users = await _repository.getUsers();
    emit(state.copyWith(users: users));
  } catch (e) {
    // Optionally show error snackbar, keep existing data
    emit(state.copyWith(refreshError: e.toString()));
  }
}
```

### Pagination

```dart
class PaginatedState<T> extends Equatable {
  final List<T> items;
  final int page;
  final bool hasReachedMax;
  final bool isLoading;

  const PaginatedState({
    this.items = const [],
    this.page = 0,
    this.hasReachedMax = false,
    this.isLoading = false,
  });

  @override
  List<Object?> get props => [items, page, hasReachedMax, isLoading];
}

class ItemsCubit extends Cubit<PaginatedState<Item>> {
  final ItemRepository _repository;

  ItemsCubit(this._repository) : super(const PaginatedState());

  Future<void> loadMore() async {
    if (state.hasReachedMax || state.isLoading) return;

    emit(state.copyWith(isLoading: true));

    final newItems = await _repository.getItems(page: state.page);

    emit(PaginatedState(
      items: [...state.items, ...newItems],
      page: state.page + 1,
      hasReachedMax: newItems.isEmpty,
      isLoading: false,
    ));
  }
}
```

---

## BLoC When Needed

Use full BLoC pattern when you need event transformation.

### Debounced Search

```dart
// Events
sealed class SearchEvent extends Equatable {
  const SearchEvent();
}

class SearchQueryChanged extends SearchEvent {
  final String query;
  const SearchQueryChanged(this.query);
  @override
  List<Object?> get props => [query];
}

// BLoC with debounce
class SearchBloc extends Bloc<SearchEvent, SearchState> {
  final SearchRepository _repository;

  SearchBloc(this._repository) : super(const SearchState()) {
    on<SearchQueryChanged>(
      _onQueryChanged,
      transformer: debounce(const Duration(milliseconds: 300)),
    );
  }

  Future<void> _onQueryChanged(
    SearchQueryChanged event,
    Emitter<SearchState> emit,
  ) async {
    if (event.query.isEmpty) {
      emit(const SearchState());
      return;
    }

    emit(state.copyWith(status: SearchStatus.loading));

    try {
      final results = await _repository.search(event.query);
      emit(state.copyWith(
        status: SearchStatus.success,
        results: results,
      ));
    } catch (e) {
      emit(state.copyWith(status: SearchStatus.failure));
    }
  }
}

// Debounce transformer
EventTransformer<T> debounce<T>(Duration duration) {
  return (events, mapper) => events.debounceTime(duration).flatMap(mapper);
}
```

---

## Testing Cubits

### Basic Test

```dart
import 'package:bloc_test/bloc_test.dart';
import 'package:test/test.dart';

void main() {
  group('CounterCubit', () {
    test('initial state is 0', () {
      expect(CounterCubit().state, equals(0));
    });

    blocTest<CounterCubit, int>(
      'emits [1] when increment is called',
      build: () => CounterCubit(),
      act: (cubit) => cubit.increment(),
      expect: () => [1],
    );

    blocTest<CounterCubit, int>(
      'emits [1, 2, 3] when increment is called 3 times',
      build: () => CounterCubit(),
      act: (cubit) {
        cubit.increment();
        cubit.increment();
        cubit.increment();
      },
      expect: () => [1, 2, 3],
    );
  });
}
```

### Testing with Dependencies

```dart
import 'package:mocktail/mocktail.dart';

class MockUserRepository extends Mock implements UserRepository {}

void main() {
  late MockUserRepository mockRepository;

  setUp(() {
    mockRepository = MockUserRepository();
  });

  blocTest<UsersCubit, UsersState>(
    'emits [loading, success] when loadUsers succeeds',
    setUp: () {
      when(() => mockRepository.getUsers())
          .thenAnswer((_) async => [User(id: '1', name: 'Test')]);
    },
    build: () => UsersCubit(mockRepository),
    act: (cubit) => cubit.loadUsers(),
    expect: () => [
      const UsersState(status: UsersStatus.loading),
      isA<UsersState>()
          .having((s) => s.status, 'status', UsersStatus.success)
          .having((s) => s.users.length, 'users length', 1),
    ],
  );
}
```

---

## Provider Patterns

### Scoped Providers

```dart
// Feature-level provider
class UserFeature extends StatelessWidget {
  const UserFeature({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => UserCubit(
        context.read<UserRepository>(),
      )..loadUser(),
      child: const UserPage(),
    );
  }
}
```

### Multi-Provider at App Level

```dart
MultiBlocProvider(
  providers: [
    BlocProvider(create: (_) => AuthCubit(authRepository)),
    BlocProvider(create: (_) => ThemeCubit()),
    BlocProvider(create: (_) => LocaleCubit()),
  ],
  child: const MyApp(),
)
```

### Lazy vs Eager

```dart
// Lazy (default) - created when first accessed
BlocProvider(
  create: (context) => ExpensiveCubit(),
  child: child,
)

// Eager - created immediately
BlocProvider(
  lazy: false,
  create: (context) => AnalyticsCubit()..initialize(),
  child: child,
)
```

---

## Common Patterns

### Form Cubit

```dart
class LoginCubit extends Cubit<LoginState> {
  final AuthRepository _authRepository;

  LoginCubit(this._authRepository) : super(const LoginState());

  void emailChanged(String email) {
    emit(state.copyWith(
      email: email,
      status: FormStatus.initial,
    ));
  }

  void passwordChanged(String password) {
    emit(state.copyWith(
      password: password,
      status: FormStatus.initial,
    ));
  }

  Future<void> submit() async {
    if (!state.isValid) return;

    emit(state.copyWith(status: FormStatus.loading));

    try {
      await _authRepository.login(
        email: state.email,
        password: state.password,
      );
      emit(state.copyWith(status: FormStatus.success));
    } catch (e) {
      emit(state.copyWith(
        status: FormStatus.failure,
        errorMessage: e.toString(),
      ));
    }
  }
}
```

### Listening for Side Effects

```dart
BlocListener<LoginCubit, LoginState>(
  listenWhen: (previous, current) => previous.status != current.status,
  listener: (context, state) {
    if (state.status == FormStatus.success) {
      context.go('/home');
    } else if (state.status == FormStatus.failure) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(state.errorMessage ?? 'Error')),
      );
    }
  },
  child: const LoginForm(),
)
```

### Combined Builder + Listener

```dart
BlocConsumer<LoginCubit, LoginState>(
  listenWhen: (previous, current) => previous.status != current.status,
  listener: (context, state) {
    if (state.status == FormStatus.failure) {
      showErrorDialog(context, state.errorMessage);
    }
  },
  buildWhen: (previous, current) => previous.status != current.status,
  builder: (context, state) {
    return state.status == FormStatus.loading
        ? const LoadingIndicator()
        : const LoginForm();
  },
)
```
