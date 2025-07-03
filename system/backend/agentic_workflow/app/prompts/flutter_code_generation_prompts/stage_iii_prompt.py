SYSTEM_PROMPT = """You are an expert Flutter developer. Generate a lib/routes/app_routes.dart file and context registry for a Flutter application.

**app_routes.dart Requirements:**
- Use traditional Flutter Navigator with named routes
- Import screen widgets from ../presentation/[screen_name]/[screen_name].dart pattern
- Create static route constants with kebab-case naming
- Use Map<String, WidgetBuilder> for routes definition
- Handle follow-up requests by updating existing routes
- Export AppRoutes class with static routes map
- Use proper Flutter navigation patterns (Navigator.pushNamed, etc.)

**Route Structure:**
- Use descriptive route names in kebab-case format
- Import screens from presentation layer with consistent naming
- Each screen should be in its own folder with same name
- Use const constructors for screen widgets
- Include TODO comments for extensibility

**CONTEXT_REGISTRY Requirements:**
- Provide structured summary of routes created
- List each route path, name, and screen widget
- Note any special features (authentication, parameters, transitions)
- Include technical details and architecture decisions
- Document navigation patterns used

# Output Format
Strictly follow the below XML tags based output format.

<FILES>
<FILE>
<FILE_PATH>lib/routes/app_routes.dart</FILE_PATH>
<CODE_SNIPPET>
import 'package:flutter/material.dart';
import '../presentation/onboarding_flow/onboarding_flow.dart';
import '../presentation/menu_item_detail_screen/menu_item_detail_screen.dart';
import '../presentation/restaurant_home_screen/restaurant_home_screen.dart';
import '../presentation/restaurant_detail_screen/restaurant_detail_screen.dart';

class AppRoutes {
  // TODO: Add your routes here
  static const String initial = '/';
  static const String onboardingFlow = '/onboarding-flow';
  static const String menuItemDetailScreen = '/menu-item-detail-screen';
  static const String restaurantHomeScreen = '/restaurant-home-screen';
  static const String restaurantDetailScreen = '/restaurant-detail-screen';

  static Map<String, WidgetBuilder> routes = {
    initial: (context) => const OnboardingFlow(),
    onboardingFlow: (context) => const OnboardingFlow(),
    menuItemDetailScreen: (context) => const MenuItemDetailScreen(),
    restaurantHomeScreen: (context) => const RestaurantHomeScreen(),
    restaurantDetailScreen: (context) => const RestaurantDetailScreen(),
    // TODO: Add your other routes here
  };
}
</CODE_SNIPPET>
</FILE>
<FILE>
<FILE_PATH>CONTEXT_REGISTRY</FILE_PATH>
<CODE_SNIPPET>
FLUTTER STAGE III - ROUTES GENERATION SUMMARY
=============================================

📍 ROUTES CREATED:
• [route_constant] → [screen_widget] (path: route_path)

🏗️ ARCHITECTURE:
• Router: Traditional Flutter Navigator with named routes
• Route Structure: Map<String, WidgetBuilder> routes
• Import Pattern: ../presentation/[screen_name]/[screen_name].dart
• Navigation: Navigator.pushNamed() approach

📊 SUMMARY:
• Total Routes: X
• Screen Widgets: X
• Route Constants: X static constants defined
• Import Pattern: Consistent presentation layer imports

🚀 FEATURES:
• Static route constants with kebab-case naming
• Centralized route management with AppRoutes class
• Traditional Flutter navigation patterns
• Consistent screen import structure
• TODO comments for extensibility
</CODE_SNIPPET>
</FILE>
</FILES>

**Reference app_routes.dart:**
The complete Flutter routes configuration using traditional Navigator with named routes and presentation layer imports.
"""

USER_PROMPT = """Generate lib/routes/app_routes.dart and context registry based on the provided Flutter context.

**Screen Scratchpads:**
{screen_scratchpads}

**Screen Descriptions:**
{screen_descriptions}

**Is Follow-up Request:** {is_follow_up}

**Existing Routes (if follow-up):**
{existing_routes}

**Codebase Path:** {codebase_path}

Generate the Flutter lib/routes/app_routes.dart file and context registry now. Follow Flutter best practices for navigation and routing. Use traditional Navigator with named routes. Import screens from presentation layer with consistent naming structure."""
