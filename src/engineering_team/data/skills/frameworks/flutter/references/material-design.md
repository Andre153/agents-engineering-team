# Material Design 3 in Flutter

## Table of Contents
1. [Theme Setup](#theme-setup)
2. [Color System](#color-system)
3. [Typography](#typography)
4. [Components](#components)
5. [Spacing & Layout](#spacing--layout)
6. [Adaptive Design](#adaptive-design)
7. [Dark Mode](#dark-mode)
8. [Custom Theming](#custom-theming)

---

## Theme Setup

### Basic Material 3 Theme

```dart
import 'package:flutter/material.dart';

class AppTheme {
  static ThemeData light() {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: Colors.blue,
        brightness: Brightness.light,
      ),
    );
  }

  static ThemeData dark() {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: Colors.blue,
        brightness: Brightness.dark,
      ),
    );
  }
}

// Usage
MaterialApp(
  theme: AppTheme.light(),
  darkTheme: AppTheme.dark(),
  themeMode: ThemeMode.system,
  home: const MyHomePage(),
)
```

---

## Color System

### Semantic Colors

Material 3 uses semantic color roles. Always use these instead of hardcoded colors:

```dart
// ✅ Good - adapts to theme
Container(
  color: Theme.of(context).colorScheme.surface,
  child: Text(
    'Hello',
    style: TextStyle(color: Theme.of(context).colorScheme.onSurface),
  ),
)

// ❌ Bad - hardcoded
Container(
  color: Colors.white,
  child: Text('Hello', style: TextStyle(color: Colors.black)),
)
```

### Key Color Roles

| Role | Usage |
|------|-------|
| `primary` | Main brand color, FABs, prominent buttons |
| `onPrimary` | Text/icons on primary color |
| `primaryContainer` | Less prominent primary elements |
| `secondary` | Accents, less prominent than primary |
| `surface` | Backgrounds of cards, sheets, dialogs |
| `onSurface` | Text/icons on surface |
| `surfaceContainerHighest` | Elevated surfaces |
| `error` | Error states |
| `outline` | Borders, dividers |

### Using Colors

```dart
final colorScheme = Theme.of(context).colorScheme;

// Buttons
ElevatedButton(
  style: ElevatedButton.styleFrom(
    backgroundColor: colorScheme.primary,
    foregroundColor: colorScheme.onPrimary,
  ),
  onPressed: () {},
  child: const Text('Primary'),
)

// Cards
Card(
  color: colorScheme.surfaceContainerHighest,
  child: Text('Card content', style: TextStyle(color: colorScheme.onSurface)),
)

// Errors
Text(
  'Error message',
  style: TextStyle(color: colorScheme.error),
)
```

### Custom Color Scheme

```dart
ColorScheme.fromSeed(
  seedColor: const Color(0xFF6750A4),
  brightness: Brightness.light,
  primary: const Color(0xFF6750A4),        // Override specific colors
  secondary: const Color(0xFF625B71),
)
```

---

## Typography

### Text Theme

```dart
final textTheme = Theme.of(context).textTheme;

// Display - largest, hero text
Text('Hero', style: textTheme.displayLarge)
Text('Large Display', style: textTheme.displayMedium)
Text('Display', style: textTheme.displaySmall)

// Headlines - section titles
Text('Headline', style: textTheme.headlineLarge)
Text('Section', style: textTheme.headlineMedium)
Text('Subsection', style: textTheme.headlineSmall)

// Title - prominent text
Text('Title', style: textTheme.titleLarge)
Text('Card Title', style: textTheme.titleMedium)
Text('List Title', style: textTheme.titleSmall)

// Body - main content
Text('Body text', style: textTheme.bodyLarge)
Text('Regular text', style: textTheme.bodyMedium)
Text('Small text', style: textTheme.bodySmall)

// Label - buttons, captions
Text('BUTTON', style: textTheme.labelLarge)
Text('Caption', style: textTheme.labelMedium)
Text('Tiny', style: textTheme.labelSmall)
```

### Custom Typography

```dart
ThemeData(
  useMaterial3: true,
  textTheme: TextTheme(
    displayLarge: GoogleFonts.roboto(
      fontSize: 57,
      fontWeight: FontWeight.w400,
    ),
    // ... other styles
  ),
)
```

---

## Components

### Buttons

```dart
// Filled (primary action)
FilledButton(
  onPressed: () {},
  child: const Text('Filled'),
)

// Filled Tonal (secondary action)
FilledButton.tonal(
  onPressed: () {},
  child: const Text('Tonal'),
)

// Elevated (needs emphasis)
ElevatedButton(
  onPressed: () {},
  child: const Text('Elevated'),
)

// Outlined (medium emphasis)
OutlinedButton(
  onPressed: () {},
  child: const Text('Outlined'),
)

// Text (low emphasis)
TextButton(
  onPressed: () {},
  child: const Text('Text'),
)

// Icon buttons
IconButton(
  onPressed: () {},
  icon: const Icon(Icons.settings),
)

IconButton.filled(
  onPressed: () {},
  icon: const Icon(Icons.add),
)
```

### Cards

```dart
// Elevated Card
Card(
  elevation: 1,
  child: Padding(
    padding: const EdgeInsets.all(16),
    child: Column(
      children: [
        Text('Card Title', style: textTheme.titleMedium),
        Text('Card content goes here'),
      ],
    ),
  ),
)

// Filled Card
Card(
  elevation: 0,
  color: colorScheme.surfaceContainerHighest,
  child: /* ... */,
)

// Outlined Card
Card(
  elevation: 0,
  shape: RoundedRectangleBorder(
    side: BorderSide(color: colorScheme.outline),
    borderRadius: BorderRadius.circular(12),
  ),
  child: /* ... */,
)
```

### Text Fields

```dart
// Filled (default)
TextField(
  decoration: const InputDecoration(
    labelText: 'Label',
    hintText: 'Hint text',
    filled: true,
  ),
)

// Outlined
TextField(
  decoration: const InputDecoration(
    labelText: 'Label',
    border: OutlineInputBorder(),
  ),
)

// With icons
TextField(
  decoration: const InputDecoration(
    labelText: 'Search',
    prefixIcon: Icon(Icons.search),
    suffixIcon: Icon(Icons.clear),
  ),
)
```

### Navigation

```dart
// Bottom Navigation Bar
NavigationBar(
  selectedIndex: currentIndex,
  onDestinationSelected: (index) => setState(() => currentIndex = index),
  destinations: const [
    NavigationDestination(
      icon: Icon(Icons.home_outlined),
      selectedIcon: Icon(Icons.home),
      label: 'Home',
    ),
    NavigationDestination(
      icon: Icon(Icons.search),
      label: 'Search',
    ),
    NavigationDestination(
      icon: Icon(Icons.person_outline),
      selectedIcon: Icon(Icons.person),
      label: 'Profile',
    ),
  ],
)

// Navigation Rail (tablets/desktop)
NavigationRail(
  selectedIndex: currentIndex,
  onDestinationSelected: (index) => setState(() => currentIndex = index),
  labelType: NavigationRailLabelType.selected,
  destinations: const [
    NavigationRailDestination(
      icon: Icon(Icons.home_outlined),
      selectedIcon: Icon(Icons.home),
      label: Text('Home'),
    ),
    // ...
  ],
)

// Navigation Drawer
NavigationDrawer(
  selectedIndex: currentIndex,
  onDestinationSelected: (index) {},
  children: [
    const NavigationDrawerDestination(
      icon: Icon(Icons.home),
      label: Text('Home'),
    ),
    // ...
  ],
)
```

### Dialogs & Sheets

```dart
// Alert Dialog
showDialog(
  context: context,
  builder: (context) => AlertDialog(
    title: const Text('Dialog Title'),
    content: const Text('Dialog content here'),
    actions: [
      TextButton(
        onPressed: () => Navigator.pop(context),
        child: const Text('Cancel'),
      ),
      FilledButton(
        onPressed: () => Navigator.pop(context, true),
        child: const Text('Confirm'),
      ),
    ],
  ),
);

// Bottom Sheet
showModalBottomSheet(
  context: context,
  builder: (context) => Container(
    padding: const EdgeInsets.all(16),
    child: Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        // Content
      ],
    ),
  ),
);
```

---

## Spacing & Layout

### Standard Spacing Scale

```dart
abstract class Spacing {
  static const double xs = 4;
  static const double sm = 8;
  static const double md = 16;
  static const double lg = 24;
  static const double xl = 32;
  static const double xxl = 48;
}

// Usage
Padding(
  padding: const EdgeInsets.all(Spacing.md),
  child: /* ... */,
)

SizedBox(height: Spacing.sm)
```

### Consistent Padding

```dart
// Page padding
Padding(
  padding: const EdgeInsets.symmetric(horizontal: 16),
  child: /* ... */,
)

// Card padding
Padding(
  padding: const EdgeInsets.all(16),
  child: /* ... */,
)

// List item padding
ListTile(
  contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
  // ...
)
```

---

## Adaptive Design

### Responsive Breakpoints

```dart
abstract class Breakpoints {
  static const double compact = 600;    // Phone
  static const double medium = 840;     // Tablet portrait
  static const double expanded = 1200;  // Tablet landscape / Desktop
}

class ResponsiveLayout extends StatelessWidget {
  final Widget compact;
  final Widget? medium;
  final Widget? expanded;

  const ResponsiveLayout({
    required this.compact,
    this.medium,
    this.expanded,
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth >= Breakpoints.expanded) {
          return expanded ?? medium ?? compact;
        }
        if (constraints.maxWidth >= Breakpoints.medium) {
          return medium ?? compact;
        }
        return compact;
      },
    );
  }
}
```

### Adaptive Navigation

```dart
class AdaptiveScaffold extends StatelessWidget {
  final int selectedIndex;
  final ValueChanged<int> onDestinationSelected;
  final Widget body;

  const AdaptiveScaffold({
    required this.selectedIndex,
    required this.onDestinationSelected,
    required this.body,
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.sizeOf(context).width;

    if (width >= Breakpoints.medium) {
      // Tablet/Desktop - use NavigationRail
      return Scaffold(
        body: Row(
          children: [
            NavigationRail(
              selectedIndex: selectedIndex,
              onDestinationSelected: onDestinationSelected,
              destinations: _destinations,
            ),
            Expanded(child: body),
          ],
        ),
      );
    }

    // Phone - use bottom nav
    return Scaffold(
      body: body,
      bottomNavigationBar: NavigationBar(
        selectedIndex: selectedIndex,
        onDestinationSelected: onDestinationSelected,
        destinations: _navDestinations,
      ),
    );
  }
}
```

---

## Dark Mode

### System-Aware Theme

```dart
MaterialApp(
  theme: AppTheme.light(),
  darkTheme: AppTheme.dark(),
  themeMode: ThemeMode.system, // Follows system setting
)
```

### Manual Theme Toggle

```dart
class ThemeCubit extends Cubit<ThemeMode> {
  ThemeCubit() : super(ThemeMode.system);

  void setLight() => emit(ThemeMode.light);
  void setDark() => emit(ThemeMode.dark);
  void setSystem() => emit(ThemeMode.system);
  void toggle() => emit(
    state == ThemeMode.light ? ThemeMode.dark : ThemeMode.light,
  );
}

// In MaterialApp
BlocBuilder<ThemeCubit, ThemeMode>(
  builder: (context, themeMode) {
    return MaterialApp(
      theme: AppTheme.light(),
      darkTheme: AppTheme.dark(),
      themeMode: themeMode,
    );
  },
)
```

### Theme-Aware Images

```dart
Image.asset(
  Theme.of(context).brightness == Brightness.dark
      ? 'assets/logo_dark.png'
      : 'assets/logo_light.png',
)
```

---

## Custom Theming

### Component Themes

```dart
ThemeData(
  useMaterial3: true,
  colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),

  // Card theme
  cardTheme: CardTheme(
    elevation: 0,
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(16),
    ),
  ),

  // AppBar theme
  appBarTheme: const AppBarTheme(
    centerTitle: true,
    elevation: 0,
  ),

  // Input decoration theme
  inputDecorationTheme: InputDecorationTheme(
    filled: true,
    border: OutlineInputBorder(
      borderRadius: BorderRadius.circular(12),
    ),
  ),

  // Elevated button theme
  elevatedButtonTheme: ElevatedButtonThemeData(
    style: ElevatedButton.styleFrom(
      minimumSize: const Size(double.infinity, 48),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
    ),
  ),
)
```

### Theme Extensions

```dart
// Define extension
@immutable
class CustomColors extends ThemeExtension<CustomColors> {
  final Color success;
  final Color warning;

  const CustomColors({
    required this.success,
    required this.warning,
  });

  @override
  CustomColors copyWith({Color? success, Color? warning}) {
    return CustomColors(
      success: success ?? this.success,
      warning: warning ?? this.warning,
    );
  }

  @override
  CustomColors lerp(CustomColors? other, double t) {
    if (other is! CustomColors) return this;
    return CustomColors(
      success: Color.lerp(success, other.success, t)!,
      warning: Color.lerp(warning, other.warning, t)!,
    );
  }
}

// Add to theme
ThemeData(
  extensions: [
    const CustomColors(
      success: Color(0xFF4CAF50),
      warning: Color(0xFFFFC107),
    ),
  ],
)

// Use in widgets
final customColors = Theme.of(context).extension<CustomColors>()!;
Container(color: customColors.success)
```
