"""
Test extra features of the composition root.
"""

from dependency_injection.composition_root import CompositionRoot
from dependency_injection.di_container import DIContainer


class MockExtraService:
    """Mock extra service for testing."""

    def __init__(self) -> None:
        self.name = "extra"


def test_configure_with_extra_registrations() -> None:
    """Should apply extra registrations callback."""

    def extra_registrations(container: DIContainer) -> None:
        container.register_singleton(MockExtraService)

    # Configure with extra registrations
    container = CompositionRoot.configure(
        database_path=":memory:", extra_registrations=extra_registrations
    )

    # Should have the extra service registered
    assert container.is_registered(MockExtraService)
    extra_service = container.resolve(MockExtraService)
    assert isinstance(extra_service, MockExtraService)
    assert extra_service.name == "extra"
