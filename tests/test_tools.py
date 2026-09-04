import unittest

from src.tools.data_store import (DataStoreError,
    find_duplicate_claim,
    get_claim_by_id)


class DataStoreTests(unittest.TestCase):
    """Tests for safe reads from Problem A reference data."""

    def test_get_known_claim(self) -> None:
        """A known claim ID should return the matching claim record."""
        claim = get_claim_by_id("CLM-8842")

        self.assertEqual(claim["claim_id"], "CLM-8842")
        self.assertEqual(claim["member_id"], "M-2214")

    def test_unknown_claim_returns_clear_error(self) -> None:
        """An unknown claim ID should raise a clear structured error."""
        with self.assertRaisesRegex(DataStoreError, "CLAIM_NOT_FOUND"):
            get_claim_by_id("CLM-9999")

    def test_true_duplicate_matches_prior_claim(self) -> None:
        """A real duplicate should match the correct historical claim."""
        claim = get_claim_by_id("CLM-8933")

        prior_claim = find_duplicate_claim(
            claim["member_id"],
            claim["hospital_id"],
            claim["date_of_service"],
            claim["lines"],
        )

        self.assertIsNotNone(prior_claim)
        self.assertEqual(prior_claim["claim_id"], "CLM-8710")

    def test_date_near_miss_is_not_duplicate(self) -> None:
        """A claim differing only in service date must not be a duplicate."""
        claim = get_claim_by_id("CLM-8850")

        prior_claim = find_duplicate_claim(
            claim["member_id"],
            claim["hospital_id"],
            claim["date_of_service"],
            claim["lines"],
        )

        self.assertIsNone(prior_claim)

    def test_line_items_near_miss_is_not_duplicate(self) -> None:
        """A claim with different line items must not be a duplicate."""
        claim = get_claim_by_id("CLM-8960")

        prior_claim = find_duplicate_claim(
            claim["member_id"],
            claim["hospital_id"],
            claim["date_of_service"],
            claim["lines"],
        )

        self.assertIsNone(prior_claim)