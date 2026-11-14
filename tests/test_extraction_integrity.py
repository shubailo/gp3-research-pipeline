import unittest
from src.validate_extraction_integrity import ExtractionIntegrityAuditor

class TestExtractionIntegrity(unittest.TestCase):
    def test_auditor_init(self):
        auditor = ExtractionIntegrityAuditor("dummy_path.xlsx")
        self.assertEqual(auditor.wb_path, "dummy_path.xlsx")

if __name__ == '__main__':
    unittest.main()

