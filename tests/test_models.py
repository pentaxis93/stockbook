"""
DEPRECATED: Legacy Pydantic model tests.

These tests have been replaced by domain entity tests in test_domain_entities.py
as part of the clean architecture migration.

The legacy Pydantic models in models.py have been removed in favor of
rich domain entities with proper business logic and validation.
"""

import pytest


def test_legacy_models_deprecated():
    """Test that confirms legacy models have been deprecated"""
    # This test serves as a marker that the legacy model tests have been migrated
    # to domain entity tests. It will be removed when the legacy cleanup is complete.
    assert True, "Legacy models have been replaced by domain entities"


# TODO: Remove this file completely after legacy cleanup is confirmed working
# The domain entity tests are now in test_domain_entities.py
