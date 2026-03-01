import unittest
from pathlib import Path
from src.services.scanner import scan_downloads

class TestScanner(unittest.TestCase):
    def test_scan_downloads_structure(self):
        result = scan_downloads()
        self.assertIn('total_files', result)
        self.assertIn('total_size', result)
        self.assertIn('by_category', result)
        self.assertIn('by_extension', result)

if __name__ == '__main__':
    unittest.main()
