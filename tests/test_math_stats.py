import unittest
import math

class TestMathStatsUtils(unittest.TestCase):
    def test_calculate_cohens_kappa_counts(self):
        from src.utils.math_stats import calculate_cohens_kappa
        # 10 both include, 80 both exclude, 5 r1 only, 5 r2 only -> total 100
        res = calculate_cohens_kappa(10, 80, 5, 5)
        self.assertIn('kappa', res)
        self.assertIn('interpretation', res)
        self.assertGreater(res['kappa'], 0.5)
        self.assertEqual(res['total'], 100)

    def test_calculate_cohens_kappa_lists(self):
        from src.utils.math_stats import calculate_cohens_kappa_from_lists
        r1 = ['INCLUDE', 'INCLUDE', 'EXCLUDE', 'EXCLUDE']
        r2 = ['INCLUDE', 'EXCLUDE', 'INCLUDE', 'EXCLUDE']
        res = calculate_cohens_kappa_from_lists(r1, r2)
        self.assertIn('kappa', res)
        self.assertIn('percent_agreement', res)

    def test_calculate_odds_ratio_2x2(self):
        from src.utils.math_stats import calculate_odds_ratio
        # Intervention: 10/100, Control: 20/100
        res = calculate_odds_ratio(a=10, total_intervention=100, c=20, total_control=100)
        self.assertIn('or', res)
        self.assertIn('log_or', res)
        self.assertIn('se', res)
        self.assertIn('ci_min', res)
        self.assertIn('ci_max', res)
        # 10*80 / (90*20) = 800 / 1800 = 0.444...
        self.assertAlmostEqual(res['or'], 800/1800, places=3)

    def test_calculate_odds_ratio_zero_cell_correction(self):
        from src.utils.math_stats import calculate_odds_ratio
        # Zero event in intervention
        res = calculate_odds_ratio(a=0, total_intervention=50, c=5, total_control=50)
        self.assertTrue(math.isfinite(res['or']))
        self.assertTrue(math.isfinite(res['log_or']))

    def test_calculate_or_from_ci(self):
        from src.utils.math_stats import calculate_or_from_ci
        res = calculate_or_from_ci(pe=1.5, ci_min=1.1, ci_max=2.0)
        self.assertEqual(res['or'], 1.5)
        self.assertAlmostEqual(res['log_or'], math.log(1.5), places=4)
        self.assertGreater(res['se'], 0)

    def test_pool_random_effects(self):
        from src.utils.math_stats import pool_random_effects
        studies = [
            {'study': 'S1', 'log_or': 0.2, 'var': 0.04},
            {'study': 'S2', 'log_or': 0.3, 'var': 0.05},
            {'study': 'S3', 'log_or': 0.25, 'var': 0.03}
        ]
        res = pool_random_effects(studies)
        self.assertIsNotNone(res)
        self.assertEqual(res['k'], 3)
        self.assertIn('or', res)
        self.assertIn('I2', res)
        self.assertIn('tau2', res)
        self.assertGreater(res['or'], 1.0)

if __name__ == '__main__':
    unittest.main()
