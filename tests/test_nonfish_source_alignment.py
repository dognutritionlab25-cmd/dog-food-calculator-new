import unittest

from nutrition_core import calculate, catalog_data, make_request


AA_EXPECTED = {
    "소간(생)": {"히스티딘": 629, "아르기닌": 1241},
    "소비장(생)": {"류신": 1616, "이소류신": 706, "발린": 1101, "페닐알라닌": 735, "티로신": 521, "트레오닌": 720, "메티오닌": 337, "리신": 1323, "트립토판": 190, "히스티딘": 656, "아르기닌": 1060},
    "닭간(생)": {"히스티딘": 507, "아르기닌": 1093},
    "소고기(lean)": {"류신": 1627, "이소류신": 922, "발린": 1025, "페닐알라닌": 814, "티로신": 642, "트레오닌": 807, "메티오닌": 537, "리신": 1728, "트립토판": 106, "히스티딘": 678, "아르기닌": 1358},
    "계란노른자(생)": {"류신": 1399, "이소류신": 866, "발린": 949, "페닐알라닌": 681, "티로신": 678, "트레오닌": 687, "메티오닌": 378, "리신": 1217, "트립토판": 177, "히스티딘": 416, "아르기닌": 1099},
    "양고기(lean,다리)": {"류신": 1418, "이소류신": 881, "발린": 983, "페닐알라닌": 741, "티로신": 613, "트레오닌": 779, "메티오닌": 467, "리신": 1611, "트립토판": 213, "히스티딘": 578, "아르기닌": 1082},
}


class NonFishSourceAlignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = catalog_data()
        cls.rows = {row["재료명"]: row for row in cls.catalog["db_data"]}

    def test_manifest_amino_values(self):
        for key, expected in AA_EXPECTED.items():
            for nutrient, value in expected.items():
                self.assertEqual(self.catalog["amino_db"][key][nutrient], value, f"{key} {nutrient}")

    def test_manifest_vitamin_e_values(self):
        self.assertEqual(self.rows["닭간 (Chicken Liver)"]["비타민E"], 1.045)
        self.assertEqual(self.rows["소고기 (Beef)"]["비타민E"], 0.254)
        self.assertEqual(self.rows["계란노른자 (Egg Yolk)"]["비타민E"], 3.851)

    def test_iodine_and_hold_rows_are_unchanged(self):
        self.assertEqual(self.rows["닭간 (Chicken Liver)"]["요오드(mcg)"], 3.67)
        self.assertEqual(self.rows["소고기 (Beef)"]["요오드(mcg)"], 0)
        self.assertEqual(self.rows["계란노른자 (Egg Yolk)"]["요오드(mcg)"], 63.7)
        self.assertEqual(self.catalog["amino_db"]["닭가슴살(생,껍질제)"]["류신"], 1510)
        self.assertEqual(self.catalog["amino_db"]["말고기(lean,생)"]["류신"], 1720)
        self.assertEqual(self.catalog["amino_db"]["사슴고기(lean,생)"]["류신"], 2280)
        self.assertEqual(self.catalog["amino_db"]["소심장(생)"]["류신"], 1700)
        self.assertEqual(self.catalog["amino_db"]["칠면조가슴살(생)"]["류신"], 1310)
        self.assertEqual(self.catalog["amino_db"]["오리고기(lean,생)"]["류신"], 1544)
        self.assertEqual(self.catalog["amino_db"]["염소고기(lean)"]["류신"], 1716)

    def test_snapshot_result_shape_remains_available(self):
        result = calculate(make_request({"소고기 (Beef)": 100}), "review")
        self.assertIn("food_db_version", result)
        self.assertIn("calculation_policy_version", result)


if __name__ == "__main__":
    unittest.main()
