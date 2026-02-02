# GoRouter Navigation Patterns

## Table of Contents
1. [Setup](#setup)
2. [Basic Routes](#basic-routes)
3. [Parameters](#parameters)
4. [Nested Navigation](#nested-navigation)
5. [Guards & Redirects](#guards--redirects)
6. [Deep Linking](#deep-linking)
7. [Type-Safe Routes](#type-safe-routes)
8. [Shell Routes](#shell-routes)
9. [Transitions](#transitions)

---

## Setup

### Installation

```yaml
dependencies:
  go_router: ^13.0.0
```

### Basic Configuration

```dart
import 'package:go_router/go_router.dart';

final appRouter = GoRouter(
  initialLocation: '/',
  debugLogDiagnostics: true, // Remove in production
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => const HomePage(),
    ),
  ],
);

// In MaterialApp
class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      routerConfig: appRouter,
      title: 'My App',
      theme: ThemeData(useMaterial3: true),
    );
  }
}
```

---

## Basic Routes

### Flat Routes

```dart
final appRouter = GoRouter(
  routes: [
    GoRoute(
      path: '/',
      name: 'home',
      builder: (context, state) => const HomePage(),
    ),
    GoRoute(
      path: '/settings',
      name: 'settings',
      builder: (context, state) => const SettingsPage(),
    ),
    GoRoute(
      path: '/profile',
      name: 'profile',
      builder: (context, state) => const ProfilePage(),
    ),
  ],
);
```

### Navigation Methods

```dart
// Go - replaces entire navigation stack
context.go('/settings');
context.goNamed('settings');

// Push - adds to navigation stack
context.push('/settings');
context.pushNamed('settings');

// Pop - goes back
context.pop();

// Pop with result
context.pop(result);

// Check if can pop
if (context.canPop()) {
  context.pop();
}

// Replace current route
context.pushReplacement('/new-page');
```

---

## Parameters

### Path Parameters

```dart
GoRoute(
  path: '/user/:userId',
  name: 'user',
  builder: (context, state) {
    final userId = state.pathParameters['userId']!;
    return UserPage(userId: userId);
  },
),

// Navigate
context.go('/user/123');
context.goNamed('user', pathParameters: {'userId': '123'});
```

### Query Parameters

```dart
GoRoute(
  path: '/search',
  name: 'search',
  builder: (context, state) {
    final query = state.uri.queryParameters['q'] ?? '';
    final page = int.tryParse(state.uri.queryParameters['page'] ?? '1') ?? 1;
    return SearchPage(query: query, page: page);
  },
),

// Navigate
context.go('/search?q=flutter&page=2');
context.goNamed('search', queryParameters: {'q': 'flutter', 'page': '2'});
```

### Extra Data (Non-URL State)

```dart
// Pass complex objects
context.go('/details', extra: myComplexObject);

// Receive in builder
GoRoute(
  path: '/details',
  builder: (context, state) {
    final data = state.extra as MyComplexObject?;
    return DetailsPage(data: data);
  },
),
```

⚠️ **Warning**: Extra data is lost on page refresh and deep links. Use for transient state only.

---

## Nested Navigation

### Sub-Routes

```dart
GoRoute(
  path: '/shop',
  builder: (context, state) => const ShopPage(),
  routes: [
    GoRoute(
      path: 'product/:id',  // Full path: /shop/product/:id
      builder: (context, state) {
        final id = state.pathParameters['id']!;
        return ProductPage(id: id);
      },
    ),
    GoRoute(
      path: 'cart',  // Full path: /shop/cart
      builder: (context, state) => const CartPage(),
    ),
  ],
),
```

---

## Guards & Redirects

### Global Redirect

```dart
final appRouter = GoRouter(
  redirect: (context, state) {
    final isLoggedIn = authCubit.state.isAuthenticated;
    final isLoggingIn = state.matchedLocation == '/login';

    // Redirect to login if not authenticated
    if (!isLoggedIn && !isLoggingIn) {
      return '/login?redirect=${state.matchedLocation}';
    }

    // Redirect to home if already authenticated and on login
    if (isLoggedIn && isLoggingIn) {
      return '/';
    }

    // No redirect
    return null;
  },
  routes: [...],
);
```

### Route-Level Redirect

```dart
GoRoute(
  path: '/admin',
  redirect: (context, state) {
    final isAdmin = authCubit.state.user?.isAdmin ?? false;
    if (!isAdmin) return '/unauthorized';
    return null;
  },
  builder: (context, state) => const AdminPage(),
),
```

### Reactive Auth with RefreshListenable

```dart
class AuthNotifier extends ChangeNotifier {
  bool _isAuthenticated = false;

  bool get isAuthenticated => _isAuthenticated;

  void login() {
    _isAuthenticated = true;
    notifyListeners();
  }

  void logout() {
    _isAuthenticated = false;
    notifyListeners();
  }
}

final authNotifier = AuthNotifier();

final appRouter = GoRouter(
  refreshListenable: authNotifier,
  redirect: (context, state) {
    final isLoggedIn = authNotifier.isAuthenticated;
    final isOnLogin = state.matchedLocation == '/login';

    if (!isLoggedIn && !isOnLogin) return '/login';
    if (isLoggedIn && isOnLogin) return '/';
    return null;
  },
  routes: [...],
);
```

### With BLoC

```dart
class GoRouterRefreshStream extends ChangeNotifier {
  GoRouterRefreshStream(Stream<dynamic> stream) {
    _subscription = stream.listen((_) => notifyListeners());
  }

  late final StreamSubscription<dynamic> _subscription;

  @override
  void dispose() {
    _subscription.cancel();
    super.dispose();
  }
}

// Usage
final appRouter = GoRouter(
  refreshListenable: GoRouterRefreshStream(authBloc.stream),
  redirect: (context, state) {
    // Check authBloc.state
  },
  routes: [...],
);
```

---

## Deep Linking

GoRouter handles deep links automatically. Configure in platform settings:

### Android (android/app/src/main/AndroidManifest.xml)

```xml
<intent-filter>
  <action android:name="android.intent.action.VIEW"/>
  <category android:name="android.intent.category.DEFAULT"/>
  <category android:name="android.intent.category.BROWSABLE"/>
  <data android:scheme="myapp" android:host="open"/>
  <data android:scheme="https" android:host="myapp.com"/>
</intent-filter>
```

### iOS (ios/Runner/Info.plist)

```xml
<key>CFBundleURLTypes</key>
<array>
  <dict>
    <key>CFBundleURLSchemes</key>
    <array>
      <string>myapp</string>
    </array>
  </dict>
</array>
```

---

## Type-Safe Routes

### Route Constants

```dart
abstract class AppRoutes {
  static const home = '/';
  static const login = '/login';
  static const settings = '/settings';
  static String user(String id) => '/user/$id';
  static String product(String id) => '/product/$id';
}

// Usage
context.go(AppRoutes.user('123'));
```

### Typed Extra Data

```dart
// Define typed route data
@immutable
class ProductRouteData {
  final String productId;
  final String? referrer;

  const ProductRouteData({
    required this.productId,
    this.referrer,
  });
}

// Usage
context.go('/product', extra: ProductRouteData(productId: '123'));

// In builder
final data = state.extra as ProductRouteData?;
```

---

## Shell Routes

For persistent UI elements (bottom nav, side drawer):

```dart
final appRouter = GoRouter(
  routes: [
    ShellRoute(
      builder: (context, state, child) {
        return ScaffoldWithNavBar(child: child);
      },
      routes: [
        GoRoute(
          path: '/home',
          builder: (context, state) => const HomePage(),
        ),
        GoRoute(
          path: '/search',
          builder: (context, state) => const SearchPage(),
        ),
        GoRoute(
          path: '/profile',
          builder: (context, state) => const ProfilePage(),
        ),
      ],
    ),
  ],
);

// ScaffoldWithNavBar
class ScaffoldWithNavBar extends StatelessWidget {
  final Widget child;
  const ScaffoldWithNavBar({required this.child, super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: child,
      bottomNavigationBar: NavigationBar(
        selectedIndex: _calculateIndex(context),
        onDestinationSelected: (index) => _onTap(context, index),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.search), label: 'Search'),
          NavigationDestination(icon: Icon(Icons.person), label: 'Profile'),
        ],
      ),
    );
  }

  int _calculateIndex(BuildContext context) {
    final location = GoRouterState.of(context).matchedLocation;
    if (location.startsWith('/home')) return 0;
    if (location.startsWith('/search')) return 1;
    if (location.startsWith('/profile')) return 2;
    return 0;
  }

  void _onTap(BuildContext context, int index) {
    switch (index) {
      case 0: context.go('/home');
      case 1: context.go('/search');
      case 2: context.go('/profile');
    }
  }
}
```

### Nested Shell Routes (Stateful Navigation)

```dart
final _rootNavigatorKey = GlobalKey<NavigatorState>();
final _shellNavigatorKey = GlobalKey<NavigatorState>();

final appRouter = GoRouter(
  navigatorKey: _rootNavigatorKey,
  routes: [
    ShellRoute(
      navigatorKey: _shellNavigatorKey,
      builder: (context, state, child) => ScaffoldWithNavBar(child: child),
      routes: [
        GoRoute(
          path: '/home',
          parentNavigatorKey: _shellNavigatorKey, // Shows in shell
          builder: (context, state) => const HomePage(),
        ),
      ],
    ),
    GoRoute(
      path: '/login',
      parentNavigatorKey: _rootNavigatorKey, // Full screen, no shell
      builder: (context, state) => const LoginPage(),
    ),
  ],
);
```

---

## Transitions

### Custom Page Transition

```dart
GoRoute(
  path: '/details',
  pageBuilder: (context, state) {
    return CustomTransitionPage(
      key: state.pageKey,
      child: const DetailsPage(),
      transitionsBuilder: (context, animation, secondaryAnimation, child) {
        return FadeTransition(
          opacity: animation,
          child: child,
        );
      },
    );
  },
),
```

### Slide Transition

```dart
pageBuilder: (context, state) {
  return CustomTransitionPage(
    key: state.pageKey,
    child: const DetailsPage(),
    transitionsBuilder: (context, animation, secondaryAnimation, child) {
      const begin = Offset(1.0, 0.0);
      const end = Offset.zero;
      final tween = Tween(begin: begin, end: end)
          .chain(CurveTween(curve: Curves.easeInOut));
      return SlideTransition(
        position: animation.drive(tween),
        child: child,
      );
    },
  );
},
```

### No Transition

```dart
pageBuilder: (context, state) {
  return NoTransitionPage(
    key: state.pageKey,
    child: const SettingsPage(),
  );
},
```
