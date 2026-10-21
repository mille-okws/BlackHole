"""Regression checks for the single application entrypoint."""

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import main


class EntrypointTests(unittest.TestCase):
    def test_failed_physics_returns_failure_without_rendering(self):
        with patch.object(main, "run_validation", return_value={"physics": False}), \
                patch.object(main, "run_renderer") as render, \
                redirect_stderr(StringIO()):
            self.assertEqual(main.main([]), 1)
            render.assert_not_called()

    def test_empty_validation_is_not_success(self):
        with patch.object(main, "run_validation", return_value={}), \
                patch.object(main, "run_renderer") as render, \
                redirect_stderr(StringIO()):
            self.assertEqual(main.main([]), 1)
            render.assert_not_called()

    def test_validate_only_does_not_load_renderer(self):
        with patch.object(main, "run_validation", return_value={"physics": True}), \
                patch.object(main, "run_renderer") as render, \
                redirect_stdout(StringIO()):
            self.assertEqual(main.main(["--validate-only"]), 0)
            render.assert_not_called()

    def test_missing_dependency_has_actionable_error(self):
        error = StringIO()
        with patch.object(main, "run_validation", side_effect=ModuleNotFoundError(name="scipy")), \
                redirect_stderr(error):
            self.assertEqual(main.main([]), 1)
        self.assertIn("scipy", error.getvalue())
        self.assertIn("pip install -r", error.getvalue())

    def test_headless_render_creates_nonempty_image_and_closes_figure(self):
        from PIL import Image, ImageStat

        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "nested" / "scene.png"
            with redirect_stdout(StringIO()):
                main.run_renderer(headless=True, output=destination, width=161, height=121)
            with Image.open(destination) as image:
                self.assertEqual(image.format, "PNG")
                self.assertGreater(image.width, 100)
                self.assertGreater(image.height, 100)
                self.assertGreater(max(ImageStat.Stat(image.convert("RGB")).var), 0)
                self.assertEqual(image.size, (161, 121))
                self.assertEqual(image.convert("RGB").getpixel((80, 60)), (0, 0, 0))
            import matplotlib.pyplot as plt
            self.assertEqual(plt.get_fignums(), [])


if __name__ == "__main__":
    unittest.main()
