"""
StockBook - Personal Stock Trading Tracker
Clean Architecture Main Application

This is the new main entry point that integrates the complete clean architecture
implementation with the Streamlit UI framework.
"""

from typing import Optional

import streamlit as st

from config import config
from dependency_injection.composition_root import CompositionRoot
from dependency_injection.di_container import DIContainer
from src.presentation.coordinators.stock_page_coordinator import StockPageCoordinator


class StockBookApp:
    """
    Main application class that bootstraps the dependency injection container
    and coordinates the UI presentation layer.
    """

    def __init__(self, container: Optional[DIContainer] = None):
        """Initialize the application with dependency injection container."""
        self.container = container or self._configure_dependencies()
        self._setup_streamlit()

    def _configure_dependencies(self) -> DIContainer:
        """Configure and return the dependency injection container."""
        return CompositionRoot.configure(database_path=str(config.db_path))

    def _setup_streamlit(self) -> None:
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title=config.streamlit_config["page_title"],
            page_icon=config.streamlit_config["page_icon"],
            layout=config.streamlit_config["layout"],  # type: ignore
            initial_sidebar_state=config.streamlit_config["initial_sidebar_state"],  # type: ignore
        )

        # Initialize session state for clean architecture integration
        if "app_initialized" not in st.session_state:
            st.session_state.app_initialized = True
            st.session_state.container = self.container

    def get_container(self) -> DIContainer:
        """Get the dependency injection container."""
        return self.container

    def run(self) -> None:
        """Run the main application."""
        # Title and header
        st.title("📈 StockBook")
        st.markdown("*Personal Stock Trading Tracker - Clean Architecture Edition*")

        # Sidebar navigation
        with st.sidebar:
            st.header("Navigation")
            page = st.radio(
                "Go to",
                ["Dashboard", "Stocks", "Portfolio", "Trades", "Analytics", "Settings"],
            )

        # Route to the appropriate page using clean architecture
        self._route_page(page)

    def _route_page(self, page: str) -> None:
        """Route to the appropriate page using presentation layer coordinators."""
        try:
            if page == "Dashboard":
                self._show_dashboard()
            elif page == "Stocks":
                self._show_stocks_page()
            elif page == "Portfolio":
                self._show_portfolio_page()
            elif page == "Trades":
                self._show_trades_page()
            elif page == "Analytics":
                self._show_analytics_page()
            elif page == "Settings":
                self._show_settings_page()
        except (ValueError, TypeError, AttributeError) as e:
            st.error(f"Error loading page: {str(e)}")
            if config.DEBUG:
                st.exception(e)

    def _show_dashboard(self) -> None:
        """Show the main dashboard."""
        st.header("📊 Dashboard")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Portfolio Value", "$0.00", "0.00%")

        with col2:
            st.metric("Total Stocks", "0", "0")

        with col3:
            st.metric("Active Positions", "0", "0")

        st.info(
            "📈 Welcome to StockBook! Start by adding some stocks in the Stocks section."
        )

    def _show_stocks_page(self) -> None:
        """Show the stocks management page using clean architecture."""
        st.header("📈 Stock Management")

        # Get the stock page coordinator from the DI container
        coordinator = self.container.resolve(StockPageCoordinator)

        # Use the clean architecture presentation layer
        coordinator.render_stock_page()

    def _show_portfolio_page(self) -> None:
        """Show the portfolio overview page."""
        st.header("💼 Portfolio Overview")
        st.info(
            "🚧 Portfolio analytics coming soon! This will integrate with our "
            "domain services for portfolio calculations."
        )

    def _show_trades_page(self) -> None:
        """Show the trades management page."""
        st.header("📝 Trade Management")
        st.info(
            "🚧 Trade entry and management coming soon! This will use our "
            "transaction domain entities."
        )

    def _show_analytics_page(self) -> None:
        """Show the analytics and reporting page."""
        st.header("📊 Analytics & Reports")
        st.info(
            "🚧 Advanced analytics coming soon! This will leverage our shared "
            "kernel value objects and domain services."
        )

    def _show_settings_page(self) -> None:
        """Show the application settings page."""
        st.header("⚙️ Settings")

        st.subheader("Application Configuration")
        st.code(
            f"""
Database Path: {config.db_path}
Debug Mode: {config.DEBUG}
Clean Architecture: ✅ Enabled
Dependency Injection: ✅ Active
Domain Services: ✅ Available
Shared Kernel: ✅ Loaded
        """,
            language="text",
        )

        st.success("🎉 Clean Architecture integration is active!")


def main():
    """Main application entry point."""
    try:
        app = StockBookApp()
        app.run()
    except (ImportError, ModuleNotFoundError, AttributeError) as e:
        st.error(f"Failed to initialize StockBook: {str(e)}")
        if config.DEBUG:
            st.exception(e)


if __name__ == "__main__":
    main()
