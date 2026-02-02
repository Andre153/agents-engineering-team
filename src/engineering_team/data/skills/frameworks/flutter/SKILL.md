---
name: flutter
description: "Flutter development with Material Design, BLoC/Cubit state management, and GoRouter navigation. Use when building Flutter apps, implementing state management, creating navigation flows, or designing Material-compliant UIs. Covers: widget composition, Cubit patterns, typed routing, theming, and testing."
---

# Flutter Development

## Quick Reference

| Task | Guide |
|------|-------|
| State management (Cubit patterns, BLoC when needed) | See [bloc-patterns.md](references/bloc-patterns.md) |
| Navigation and routing (GoRouter) | See [routing.md](references/routing.md) |
| Material Design (theming, components, responsive) | See [material-design.md](references/material-design.md) |
| Testing (widget, Cubit, integration) | See [testing.md](references/testing.md) |
| Analysis options template | See [assets/analysis_options.yaml](assets/analysis_options.yaml) |

## Core Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| UI Framework | Material 3 | Design system, theming, components |
| State Management | flutter_bloc (Cubits) | Predictable state, separation of concerns |
| Navigation | go_router | Type-safe, declarative routing |

## Project Structure

```
lib/
├── features/
│   └── [feature_name]/
│       ├── data/
│       │   ├── repositories/
│       │   └── models/
│       ├── domain/
│       │   ├── entities/
│       │   └── use_cases/
│       ├── presentation/
│       │   ├── cubit/
│       │   ├── pages/
│       │   └── widgets/
│       └── [feature_name].dart
├── core/
│   ├── error/
│   │   └── failures.dart
│   ├── router/
│   │   └── app_router.dart
│   ├── theme/
│   │   ├── app_theme.dart
│   │   └── app_colors.dart
│   └── utils/
└── main.dart
```

## State Management: Cubit First

Prefer Cubits over full BLoC. Use BLoC only when you need event transformation or debouncing.

### When to Use What

| Scenario | Choice |
|----------|--------|
| Simple state changes (toggle, set value) | Cubit |
| Form handling | Cubit |
| API calls with loading states | Cubit |
| Event debouncing/throttling | BLoC |
| Complex event transformations | BLoC |

### Cubit Pattern

```dart
// State - immutable with copyWith
@immutable
class CounterState extends Equatable {
  final int count;
  final bool isLoading;

  const CounterState({this.count = 0, this.isLoading = false});

  CounterState copyWith({int? count, bool? isLoading}) =>
      CounterState(
        count: count ?? this.count,
        isLoading: isLoading ?? this.isLoading,
      );

  @override
  List<Object?> get props => [count, isLoading];
}

// Cubit - simple methods, no events
class CounterCubit extends Cubit<CounterState> {
  CounterCubit() : super(const CounterState());

  void increment() => emit(state.copyWith(count: state.count + 1));
  void decrement() => emit(state.copyWith(count: state.count - 1));
}
```

### Widget Integration

```dart
// Provide at appropriate scope
BlocProvider(
  create: (context) => CounterCubit(),
  child: const CounterPage(),
)

// Consume with context.watch (rebuilds) or context.read (no rebuild)
class CounterPage extends StatelessWidget {
  const CounterPage({super.key});

  @override
  Widget build(BuildContext context) {
    final count = context.watch<CounterCubit>().state.count;

    return Scaffold(
      body: Center(child: Text('$count')),
      floatingActionButton: FloatingActionButton(
        onPressed: () => context.read<CounterCubit>().increment(),
        child: const Icon(Icons.add),
      ),
    );
  }
}
```

## Navigation: GoRouter

Type-safe, declarative routing with deep linking support.

### Basic Setup

```dart
final appRouter = GoRouter(
  initialLocation: '/',
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => const HomePage(),
    ),
    GoRoute(
      path: '/user/:id',
      builder: (context, state) {
        final userId = state.pathParameters['id']!;
        return UserPage(userId: userId);
      },
    ),
  ],
);

// In MaterialApp
MaterialApp.router(routerConfig: appRouter)
```

### Navigation

```dart
// Navigate
context.go('/home');
context.push('/details');

// With parameters
context.go('/user/123');
context.goNamed('user', pathParameters: {'id': '123'});

// Pop
context.pop();
```

## Material Design 3

### Theme Setup

```dart
final appTheme = ThemeData(
  useMaterial3: true,
  colorScheme: ColorScheme.fromSeed(
    seedColor: Colors.blue,
    brightness: Brightness.light,
  ),
);

MaterialApp(
  theme: appTheme,
  darkTheme: appTheme.copyWith(
    colorScheme: ColorScheme.fromSeed(
      seedColor: Colors.blue,
      brightness: Brightness.dark,
    ),
  ),
)
```

### Use Semantic Colors

```dart
// Good - adapts to theme
color: Theme.of(context).colorScheme.primary
color: Theme.of(context).colorScheme.onSurface

// Avoid - hardcoded
color: Colors.blue
color: Colors.black
```

## Key Dependencies

```yaml
dependencies:
  flutter_bloc: ^8.1.3
  equatable: ^2.0.5
  go_router: ^13.0.0

dev_dependencies:
  bloc_test: ^9.1.5
  mocktail: ^1.0.1
```

## Code Style

### Naming
- `FeatureNameCubit` for Cubits
- `FeatureNameState` for states
- `FeatureNamePage` for full-screen widgets
- `feature_name.dart` for files

### Widget Guidelines
- Const constructors when possible
- Extract widgets at ~100 lines
- Prefer composition over inheritance
- Use named parameters for clarity
