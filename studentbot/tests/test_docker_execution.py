import unittest

class TestDockerExecution(unittest.TestCase):
    def test_import_main(self):
        """
        Test that the main module can be imported without errors.
        """
        try:
            from studentbot import main
        except Exception as e:
            self.fail(f"Failed to import main module: {e}")

if __name__ == '__main__':
    unittest.main()
