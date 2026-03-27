import unittest

from ai_generated_analyzer import AIGeneratedAnalyzer


class AIGeneratedAnalyzerTests(unittest.TestCase):
    def setUp(self):
        self.analyzer = AIGeneratedAnalyzer()

    def test_short_text_returns_low_confidence_result(self):
        analysis_result = self.analyzer.analyze_text("太短了。")
        self.assertEqual(analysis_result["score"], 0)
        self.assertIsInstance(analysis_result["conclusion"], str)
        self.assertEqual(analysis_result["patterns"], [])

    def test_analysis_result_structure_and_score_range(self):
        source_text = (
            "首先，我们需要建立统一的评估框架。其次，模型在不同样本上的表现要进行横向对比。"
            "最后，应该给出可解释性的总结。总体来说，这个过程强调结构化表达。"
            "此外，文本中会出现明显的过渡短语，进一步提高模板化程度。"
            "in conclusion, the generated response is coherent and organized."
        ) * 6
        analysis_result = self.analyzer.analyze_text(source_text)
        self.assertIn("score", analysis_result)
        self.assertIn("conclusion", analysis_result)
        self.assertIn("patterns", analysis_result)
        self.assertGreaterEqual(analysis_result["score"], 0)
        self.assertLessEqual(analysis_result["score"], 100)
        self.assertIsInstance(analysis_result["conclusion"], str)
        self.assertIsInstance(analysis_result["patterns"], list)
        for detected_pattern in analysis_result["patterns"]:
            self.assertIn("pattern", detected_pattern)
            self.assertIn("description", detected_pattern)
            self.assertIn("confidence", detected_pattern)
            self.assertIn(detected_pattern["confidence"], {"High", "Medium", "Low"})


if __name__ == "__main__":
    unittest.main()
