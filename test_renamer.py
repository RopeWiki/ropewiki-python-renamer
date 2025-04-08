#!/usr/bin/env python3
import unittest
from unittest.mock import patch, MagicMock
from renamer import Renamer

class TestRenamer(unittest.TestCase):
    @patch("renamer.mwclient.Site")  # Mock the mwclient.Site class
    def setUp(self, mock_site):
        # Mock the login method of the mwclient.Site instance
        mock_site_instance = MagicMock()
        mock_site.return_value = mock_site_instance

        # Initialize Renamer with the mocked mwclient.Site
        self.renamer = Renamer(
            site_url="dummy_url",
            username="dummy_user",
            password="dummy_pass",
            old_name="Davis Creek Canyon",
            new_name="Bob Land"
        )

        # Ensure the mocked site instance is used
        self.mock_site_instance = mock_site_instance

        self.maxDiff = None

    def test_rename_conditions(self):
        conditions = {
            "Conditions:Davis Creek Canyon-20231009060850",
            "Conditions:Davis Creek Canyon-20241009060850"
        }
        expected = [
            ("Conditions:Davis Creek Canyon-20231009060850", "Conditions:Bob Land-20231009060850"),
            ("Conditions:Davis Creek Canyon-20241009060850", "Conditions:Bob Land-20241009060850")
        ]
        result = self.renamer.rename_conditions(conditions)
        self.assertEqual(sorted(result), sorted(expected))

    def test_rename_ratings(self):
        ratings = {
            "Votes:Davis Creek Canyon/Ames",
            "Votes:Davis Creek Canyon/Smith"
        }
        expected = [
            ("Votes:Davis Creek Canyon/Ames", "Votes:Bob Land/Ames"),
            ("Votes:Davis Creek Canyon/Smith", "Votes:Bob Land/Smith")
        ]
        result = self.renamer.rename_ratings(ratings)
        self.assertEqual(sorted(result), sorted(expected))

    def test_rename_lists(self):
        lists = {
            "Lists:Fil/Davis Creek Canyon",
            "Lists:Fil/Another/Davis Creek Canyon"
        }
        expected = [
            ("Lists:Fil/Davis Creek Canyon", "Lists:Fil/Bob Land"),
            ("Lists:Fil/Another/Davis Creek Canyon", "Lists:Fil/Another/Bob Land")
        ]
        result = self.renamer.rename_lists(lists)
        self.assertEqual(sorted(result), sorted(expected))

    def test_rename_references(self):
        references = {
            "References:Davis Creek Canyon-20160624185152",
            "References:Davis Creek Canyon-20170624185152"
        }
        expected = [
            ("References:Davis Creek Canyon-20160624185152", "References:Bob Land-20160624185152"),
            ("References:Davis Creek Canyon-20170624185152", "References:Bob Land-20170624185152")
        ]
        result = self.renamer.rename_references(references)
        self.assertEqual(sorted(result), sorted(expected))

    def test_rename_incidents(self):
        incidents = {
            "Incidents:Broken hand in Davis Creek Canyon",
            "Incidents:Accident in Davis Creek Canyon"
        }
        expected = [
            ("Incidents:Broken hand in Davis Creek Canyon", "Incidents:Broken hand in Bob Land"),
            ("Incidents:Accident in Davis Creek Canyon", "Incidents:Accident in Bob Land")
        ]
        result = self.renamer.rename_incidents(incidents)
        self.assertEqual(sorted(result), sorted(expected))

if __name__ == "__main__":
    unittest.main()