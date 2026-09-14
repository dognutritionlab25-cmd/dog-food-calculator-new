import unittest
from nutrition_core import calculate, catalog_data, make_request, weight_applications
from nutrition_core.engine import _DATA

class P1OmegaPracticalTests(unittest.TestCase):
    def test_approved_omega_golden_values(self):
        for food,o6,o3 in [('아몬드 가루 ⚠️ (Almond Flour)',12.322,.003),('호박씨 가루 (Pumpkin Seeds)',20.671,.120),('캥거루 고기 (Kangaroo Meat)',.25512,.10404)]:
            result=calculate(make_request({food:100}),'review')
            self.assertEqual(result['omega6'],o6);self.assertEqual(result['omega3_food'],o3)
            self.assertAlmostEqual(result['ratios']['omega6_3'],o6/o3)
    def test_live_membership_and_hold_protection(self):
        data=catalog_data(); names={r['재료명'] for r in data['db_data']}
        for absent in ('햄프씨드 (Hemp Seeds)','정어리 (Sardine, 뼈제외/가식부/화식용)','캥거루 사태 (Kangaroo Shank)'): self.assertNotIn(absent,names)
        self.assertIn('캥거루 고기 (Kangaroo Meat)',names)
        self.assertEqual(data['omega_db']['열빙어 (Smelt)'][:2],[.11,.47])
        self.assertEqual(data['omega_db']['정어리 (Sardine, 전체/뼈포함/무염통조림/화식용)'][:2],[.11,1.48])
        self.assertEqual(data['omega_db']['정어리 (Sardine, 생/생식용)'][:2],[.28,2.1])
        self.assertEqual(data['omega_db']['연어 (Salmon)'][:2],[2.44,1.94])
        self.assertEqual(data['omega_db']['고등어 (Mackerel)'][:2],[.43,2.12])
    def test_existing_weight_exceptions_unchanged(self):
        for food in ('블루베리 (Blueberry)','당근 퓨레 (Carrot)','익힌 홍합 (Green-Lipped Mussel)'):
            row=weight_applications(make_request({food:50},cooked=True,method='삶기'))[0]
            self.assertEqual((row['input_grams'],row['applied_grams'],row['nutrition_base_grams']),(50,50,50))
    def test_legacy_foods_calculate_but_are_not_live(self):
        for food in ('캥거루 사태 (Kangaroo Shank)','햄프씨드 (Hemp Seeds)','정어리 (Sardine, 뼈제외/가식부/화식용)'):
            result=calculate(make_request({food:10},cooked=food.endswith('화식용)'),method='삶기'),'review')
            self.assertGreater(result['kcal'],0)
        self.assertEqual(_DATA['LEGACY_SNAPSHOT_FOODS']['햄프씨드 (Hemp Seeds)']['scope'],'legacy_snapshot_only')

if __name__ == '__main__': unittest.main()
