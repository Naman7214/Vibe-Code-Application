"""
Flutter Routes Generator
Generates app_routes.dart files heuristically by analyzing the lib/presentation directory structure.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class FlutterRoutesGenerator:
    """Generates app_routes.dart files based on Flutter project structure analysis."""

    def __init__(self, lib_path: str):
        """
        Initialize the Flutter routes generator.

        Args:
            lib_path: Path to the lib directory of the Flutter project
        """
        self.lib_path = Path(lib_path)
        self.presentation_path = self.lib_path / "presentation"

    def analyze_presentation_structure(self) -> List[Dict]:
        """
        Analyze the lib/presentation directory structure to extract screen information.

        Returns:
            List of screen dictionaries with name, path, and class info
        """
        screens = []

        if not self.presentation_path.exists():
            return screens

        for screen_dir in self.presentation_path.iterdir():
            if screen_dir.is_dir():
                # Check if main dart file exists (e.g., splash_screen.dart)
                main_file = screen_dir / f"{screen_dir.name}.dart"
                if main_file.exists():
                    screen_info = self._analyze_screen_directory(screen_dir)
                    if screen_info:
                        screens.append(screen_info)

        return screens

    def _analyze_screen_directory(self, screen_dir: Path) -> Optional[Dict]:
        """
        Analyze a single screen directory.

        Args:
            screen_dir: Path to the screen directory

        Returns:
            Dictionary with screen information or None if invalid
        """
        screen_name = screen_dir.name

        # Read the actual class name from the file
        main_file = screen_dir / f"{screen_name}.dart"
        actual_class_name = self._extract_class_name_from_file(main_file)

        # Fallback to generated class name if extraction fails
        if not actual_class_name:
            actual_class_name = self._snake_to_pascal_case(screen_name)

        # Generate route constant name (snake_case to camelCase)
        route_constant = self._snake_to_camel_case(screen_name)

        # Generate route path (snake_case to kebab-case)
        route_path = self._snake_to_kebab_case(screen_name)

        # Determine if this should be the initial route
        is_initial = self._is_initial_screen(screen_name)

        return {
            "name": screen_name,
            "class_name": actual_class_name,
            "route_constant": route_constant,
            "route_path": route_path,
            "import_path": f"../presentation/{screen_name}/{screen_name}.dart",
            "is_initial": is_initial,
        }

    def _extract_class_name_from_file(self, file_path: Path) -> Optional[str]:
        """
        Extract the main class name from a dart file.

        Args:
            file_path: Path to the dart file

        Returns:
            Class name if found, None otherwise
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Look for class definitions that extend StatefulWidget or StatelessWidget
            # Pattern: class SomeClassName extends StatefulWidget
            pattern = (
                r"class\s+(\w+)\s+extends\s+(?:StatefulWidget|StatelessWidget)"
            )
            matches = re.findall(pattern, content)

            if matches:
                # Return the first class found (should be the main screen class)
                return matches[0]

        except Exception:
            # If file reading fails, return None
            pass

        return None

    def _snake_to_pascal_case(self, snake_str: str) -> str:
        """
        Convert snake_case to PascalCase.

        Args:
            snake_str: String in snake_case (e.g., 'splash_screen')

        Returns:
            String in PascalCase (e.g., 'SplashScreen')
        """
        components = snake_str.split("_")
        return "".join(word.capitalize() for word in components)

    def _snake_to_camel_case(self, snake_str: str) -> str:
        """
        Convert snake_case to camelCase.

        Args:
            snake_str: String in snake_case (e.g., 'splash_screen')

        Returns:
            String in camelCase (e.g., 'splashScreen')
        """
        components = snake_str.split("_")
        return components[0] + "".join(
            word.capitalize() for word in components[1:]
        )

    def _snake_to_kebab_case(self, snake_str: str) -> str:
        """
        Convert snake_case to kebab-case for URL paths.

        Args:
            snake_str: String in snake_case (e.g., 'splash_screen')

        Returns:
            String in kebab-case (e.g., 'splash-screen')
        """
        return snake_str.replace("_", "-")

    def _is_initial_screen(self, screen_name: str) -> bool:
        """
        Determine if a screen should be the initial route.

        Args:
            screen_name: Screen directory name

        Returns:
            True if this should be the initial route
        """
        initial_indicators = [
            "splash_screen",
            "splash",
            "home",
            "home_dashboard",
            "main",
            "dashboard",
            "index",
            "landing",
        ]
        return screen_name.lower() in initial_indicators

    def generate_app_routes_dart(self) -> str:
        """
        Generate the complete app_routes.dart file content.

        Returns:
            Generated app_routes.dart file content as string
        """
        screens = self.analyze_presentation_structure()

        # Sort screens to ensure consistent order (initial screen first)
        screens.sort(key=lambda x: (not x["is_initial"], x["name"]))

        # Build imports section
        imports = []
        imports.append("import 'package:flutter/material.dart';")

        # Add screen imports
        for screen in screens:
            imports.append(f"import '{screen['import_path']}';")

        # Build route constants
        route_constants = []
        route_constants.append("  // TODO: Add your routes here")
        route_constants.append("  static const String initial = '/';")

        for screen in screens:
            route_constants.append(
                f"  static const String {screen['route_constant']} = '/{screen['route_path']}';"
            )

        # Find initial screen
        initial_screen = next(
            (s for s in screens if s["is_initial"]),
            screens[0] if screens else None,
        )

        # Build routes map
        routes_map = []
        routes_map.append("  static Map<String, WidgetBuilder> routes = {")

        if initial_screen:
            routes_map.append(
                f"    initial: (context) => const {initial_screen['class_name']}(),"
            )

        for screen in screens:
            routes_map.append(
                f"    {screen['route_constant']}: (context) => const {screen['class_name']}(),"
            )

        routes_map.append("    // TODO: Add your other routes here")
        routes_map.append("  };")

        # Build the complete file
        file_content = self._build_complete_file(
            imports, route_constants, routes_map
        )

        return file_content

    def _build_complete_file(
        self, imports: List[str], constants: List[str], routes_map: List[str]
    ) -> str:
        """
        Build the complete app_routes.dart file content.

        Args:
            imports: List of import statements
            constants: List of route constant definitions
            routes_map: List of routes map entries

        Returns:
            Complete file content
        """
        file_lines = []

        # Add imports
        file_lines.extend(imports)
        file_lines.append("")

        # Add AppRoutes class
        file_lines.append("class AppRoutes {")

        # Add route constants
        file_lines.extend(constants)
        file_lines.append("")

        # Add routes map
        file_lines.extend(routes_map)

        file_lines.append("}")

        return "\n".join(file_lines)

    def save_routes_file(self, output_path: str) -> None:
        """
        Generate and save the app_routes.dart file.

        Args:
            output_path: Path where to save the app_routes.dart file
        """
        content = self.generate_app_routes_dart()

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

    def get_routes_analysis(self) -> Dict:
        """
        Get detailed analysis of the project structure.

        Returns:
            Dictionary with analysis results
        """
        screens = self.analyze_presentation_structure()

        return {
            "screens_found": len(screens),
            "screens": screens,
            "has_routing_structure": len(screens) > 0,
            "initial_screen": next(
                (s for s in screens if s["is_initial"]), None
            ),
        }


def generate_flutter_routes_for_project(
    lib_path: str, output_path: str = None
) -> Tuple[str, Dict]:
    """
    Generate app_routes.dart file for a Flutter project.

    Args:
        lib_path: Path to the lib directory
        output_path: Optional path to save the file (if None, returns content only)

    Returns:
        Tuple of (generated_content, analysis_info)
    """
    generator = FlutterRoutesGenerator(lib_path)

    # Generate the content
    content = generator.generate_app_routes_dart()

    # Get analysis info
    analysis = generator.get_routes_analysis()

    # Save if output path provided
    if output_path:
        generator.save_routes_file(output_path)

    return content, analysis


def analyze_flutter_project_structure(lib_path: str) -> Dict:
    """
    Analyze Flutter project structure without generating files.

    Args:
        lib_path: Path to the lib directory

    Returns:
        Analysis results
    """
    generator = FlutterRoutesGenerator(lib_path)
    return generator.get_routes_analysis()


# Example usage and testing
if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) > 1:
        lib_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else None

        try:
            content, analysis = generate_flutter_routes_for_project(
                lib_path, output_path
            )

            print("app_routes.dart generated successfully!")
            print(f"Screens found: {analysis['screens_found']}")
            print(
                f"Initial screen: {analysis['initial_screen']['name'] if analysis['initial_screen'] else 'None'}"
            )

            if not output_path:
                print("\nGenerated content:")
                print(content)

        except Exception as e:
            print(f"Error generating routes: {e}")
    else:
        print(
            "Usage: python flutter_routes_generator.py <lib_path> [output_path]"
        )
