import unittest

from rename import (
    rename_conditions,
    rename_ratings,
    rename_lists,
    rename_references,
    rename_incidents,
)

class TestRenameFunctions(unittest.TestCase):
    def setUp(self):
        global OLD_NAME, NEW_NAME
        OLD_NAME = "Davis Creek Canyon"
        NEW_NAME = "Bob Land"

    def test_rename_conditions(self):
        conditions = {"Conditions:Davis Creek Canyon-20241009060850"}
        expected = [("Conditions:Davis Creek Canyon-20241009060850", "Conditions:Bob Land-20241009060850")]
        self.assertEqual(rename_conditions(conditions), expected)

    def test_rename_ratings(self):
        ratings = {"Votes:Davis Creek Canyon/Ames"}
        expected = [("Votes:Davis Creek Canyon/Ames", "Votes:Bob Land/Ames")]
        self.assertEqual(rename_ratings(ratings), expected)

    def test_rename_lists(self):
        lists = {"Lists:Fil/Davis Creek Canyon"}
        expected = [("Lists:Fil/Davis Creek Canyon", "Lists:Fil/Bob Land")]
        self.assertEqual(rename_lists(lists), expected)

    def test_rename_references(self):
        references = {"References:Davis Creek Canyon-20160624185152"}
        expected = [("References:Davis Creek Canyon-20160624185152", "References:Bob Land-20160624185152")]
        self.assertEqual(rename_references(references), expected)

    def test_rename_incidents(self):
        incidents = {"Incidents:Broken hand in Davis Creek Canyon"}
        expected = [("Incidents:Broken hand in Davis Creek Canyon", "Incidents:Broken hand in Bob Land")]
        self.assertEqual(rename_incidents(incidents), expected)

if __name__ == "__main__":
    unittest.main()