"""
Routes Generator for React Applications
Generates Routes.jsx files heuristically by analyzing the src directory structure.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple


class RoutesGenerator:
    """Generates Routes.jsx files based on project structure analysis."""

    def __init__(self, src_path: str):
        """
        Initialize the routes generator.

        Args:
            src_path: Path to the src directory of the React project
        """
        self.src_path = Path(src_path)
        self.pages_path = self.src_path / "pages"
        self.components_path = self.src_path / "components"

    def analyze_pages_structure(self) -> List[Dict]:
        """
        Analyze the pages directory structure to extract page information.

        Returns:
            List of page dictionaries with name, path, and component info
        """
        pages = []

        if not self.pages_path.exists():
            return pages

        for page_dir in self.pages_path.iterdir():
            if page_dir.is_dir():
                # Check if index.jsx exists
                index_file = page_dir / "index.jsx"
                if index_file.exists():
                    page_info = self._analyze_page_directory(page_dir)
                    if page_info:
                        pages.append(page_info)

        return pages

    def _analyze_page_directory(self, page_dir: Path) -> Optional[Dict]:
        """
        Analyze a single page directory.

        Args:
            page_dir: Path to the page directory

        Returns:
            Dictionary with page information or None if invalid
        """
        page_name = page_dir.name

        # Generate component name from directory name
        component_name = self._dir_name_to_component_name(page_name)

        # Generate route paths from directory name
        routes = self._generate_routes_from_name(page_name)

        # Determine if this should be the home page
        is_home = self._is_home_page(page_name)

        return {
            "name": page_name,
            "component_name": component_name,
            "import_path": f"./pages/{page_name}",
            "routes": routes,
            "is_home": is_home,
        }

    def _dir_name_to_component_name(self, dir_name: str) -> str:
        """
        Convert directory name to React component name.

        Args:
            dir_name: Directory name (e.g., 'main_menu', 'home-catalog')

        Returns:
            Component name (e.g., 'MainMenu', 'HomeCatalog')
        """
        # Handle both underscore and hyphen naming conventions
        parts = dir_name.replace("_", " ").replace("-", " ").split()
        return "".join(word.capitalize() for word in parts)

    def _generate_routes_from_name(self, page_name: str) -> List[str]:
        """
        Generate route paths from page name.

        Args:
            page_name: Page directory name

        Returns:
            List of route paths
        """
        routes = []

        # Convert underscores to hyphens for URL paths
        url_path = page_name.replace("_", "-")

        # Add the main route
        routes.append(f"/{url_path}")

        # Add alternative routes based on common patterns
        if page_name in ["main_menu", "home", "home-catalog"]:
            # Don't add root path here, will be handled separately
            pass
        elif page_name in ["cart-checkout", "checkout"]:
            routes.append("/cart")
        elif page_name in ["product-details", "product_details"]:
            routes.append("/product/:productId")
        elif page_name in ["game-setup", "game_setup"]:
            routes.append("/setup")
        elif page_name in ["game-board", "game_board"]:
            routes.append("/game")
        elif page_name in ["game-history", "game_history"]:
            routes.append("/history")

        return routes

    def _is_home_page(self, page_name: str) -> bool:
        """
        Determine if a page should be the home page.

        Args:
            page_name: Page directory name

        Returns:
            True if this should be the home page
        """
        home_indicators = [
            "main_menu",
            "home",
            "home-catalog",
            "index",
            "landing",
            "dashboard",
            "game-setup",
            "game_setup",
            "homepage",
            "main",
            "start",
            "welcome",
            "overview",
            "lobby",
        ]
        return page_name.lower() in home_indicators

    def _select_home_page_robust(self, pages: List[Dict]) -> Optional[Dict]:
        """
        Robustly select the home page with fallback logic.
        
        Priority order:
        1. Pages matching home indicators
        2. Fallback to first page alphabetically
        
        Args:
            pages: List of page dictionaries
            
        Returns:
            Selected home page or None if no pages
        """
        if not pages:
            return None
            
        # Priority 1: Look for pages matching home indicators
        home_page = next(
            (p for p in pages if p["is_home"]),
            None
        )
        
        if home_page:
            return home_page
        
        # Priority 2: Fallback to first page alphabetically
        fallback_page = sorted(pages, key=lambda x: x["name"])[0]
        
        # Mark fallback page as home
        fallback_page["is_home"] = True
        
        return fallback_page

    def analyze_components_structure(self) -> Dict:
        """
        Analyze the components directory structure.

        Returns:
            Dictionary with component information
        """
        components = {
            "scroll_to_top": False,
            "error_boundary": False,
            "has_ui_components": False,
        }

        if not self.components_path.exists():
            return components

        # Check for common components
        scroll_to_top_file = self.components_path / "ScrollToTop.jsx"
        error_boundary_file = self.components_path / "ErrorBoundary.jsx"
        ui_dir = self.components_path / "ui"

        # Always import these standard components - this is the modern pattern
        components["scroll_to_top"] = True  # Always true for modern React apps
        components["error_boundary"] = True  # Always true for modern React apps
        components["has_ui_components"] = ui_dir.exists() and ui_dir.is_dir()

        return components

    def generate_routes_jsx(self) -> str:
        """
        Generate the complete Routes.jsx file content.

        Returns:
            Generated Routes.jsx file content as string
        """
        pages = self.analyze_pages_structure()
        components = self.analyze_components_structure()

        # Sort pages to ensure consistent order
        pages.sort(key=lambda x: (not x["is_home"], x["name"]))

        # Build imports section
        imports = []
        imports.append('import React from "react";')
        imports.append(
            'import { BrowserRouter, Routes as RouterRoutes, Route } from "react-router-dom";'
        )

        # Add component imports
        if components["scroll_to_top"]:
            imports.append(
                'import ScrollToTop from "./components/ScrollToTop";'
            )
        if components["error_boundary"]:
            imports.append(
                'import ErrorBoundary from "./components/ErrorBoundary";'
            )

        # Add page imports
        if pages:
            imports.append("")
            imports.append("// Page imports")
            for page in pages:
                imports.append(
                    f'import {page["component_name"]} from "{page["import_path"]}";'
                )

        # Build routes section
        routes_content = []

        # Robust home page selection with fallback
        home_page = self._select_home_page_robust(pages)

        if home_page:
            component_name = home_page["component_name"]
            routes_content.append(
                f'          <Route path="/" element={{<{component_name} />}} />'
            )

        # Add all page routes
        for page in pages:
            component_name = page["component_name"]
            for route in page["routes"]:
                routes_content.append(
                    f'          <Route path="{route}" element={{<{component_name} />}} />'
                )

        # Build the complete file
        file_content = self._build_complete_file(
            imports, routes_content, components
        )

        return file_content

    def _build_complete_file(
        self, imports: List[str], routes: List[str], components: Dict
    ) -> str:
        """
        Build the complete Routes.jsx file content.

        Args:
            imports: List of import statements
            routes: List of route definitions
            components: Component availability info

        Returns:
            Complete file content
        """
        file_lines = []

        # Add imports
        file_lines.extend(imports)
        file_lines.append("")

        # Add Routes component
        file_lines.append("const Routes = () => {")
        file_lines.append("  return (")
        file_lines.append("    <BrowserRouter>")

        # Add wrapper components
        if components["error_boundary"]:
            file_lines.append("      <ErrorBoundary>")
            indent = "        "
        else:
            indent = "      "

        if components["scroll_to_top"]:
            file_lines.append(f"{indent}<ScrollToTop />")

        file_lines.append(f"{indent}<RouterRoutes>")

        # Add routes
        for route in routes:
            file_lines.append(route)

        file_lines.append(f"{indent}</RouterRoutes>")

        # Close wrapper components
        if components["error_boundary"]:
            file_lines.append("      </ErrorBoundary>")

        file_lines.append("    </BrowserRouter>")
        file_lines.append("  );")
        file_lines.append("};")
        file_lines.append("")
        file_lines.append("export default Routes;")

        return "\n".join(file_lines)

    def save_routes_file(self, output_path: str) -> None:
        """
        Generate and save the Routes.jsx file.

        Args:
            output_path: Path where to save the Routes.jsx file
        """
        content = self.generate_routes_jsx()

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

    def get_route_analysis(self) -> Dict:
        """
        Get detailed analysis of the project structure.

        Returns:
            Dictionary with analysis results
        """
        pages = self.analyze_pages_structure()
        components = self.analyze_components_structure()

        return {
            "pages_found": len(pages),
            "pages": pages,
            "components": components,
            "has_routing_structure": len(pages) > 0,
        }


def generate_routes_for_project(
    src_path: str, output_path: str = None
) -> Tuple[str, Dict]:
    """
    Generate Routes.jsx file for a React project.

    Args:
        src_path: Path to the src directory
        output_path: Optional path to save the file (if None, returns content only)

    Returns:
        Tuple of (generated_content, analysis_info)
    """
    generator = RoutesGenerator(src_path)

    # Generate the content
    content = generator.generate_routes_jsx()

    # Get analysis info
    analysis = generator.get_route_analysis()

    # Save if output path provided
    if output_path:
        generator.save_routes_file(output_path)

    return content, analysis


def analyze_project_structure(src_path: str) -> Dict:
    """
    Analyze project structure without generating files.

    Args:
        src_path: Path to the src directory

    Returns:
        Analysis results
    """
    generator = RoutesGenerator(src_path)
    return generator.get_route_analysis()


# Example usage and testing
if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) > 1:
        src_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else None

        try:
            content, analysis = generate_routes_for_project(
                src_path, output_path
            )

            print("Routes.jsx generated successfully!")
            print(f"Pages found: {analysis['pages_found']}")
            print(f"Components available: {analysis['components']}")

            if not output_path:
                print("\nGenerated content:")
                print(content)

        except Exception as e:
            print(f"Error generating routes: {e}")
    else:
        print("Usage: python routes_generator.py <src_path> [output_path]")
