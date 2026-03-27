import math
import re
from collections import Counter
from typing import Dict, List, Tuple


class AIGeneratedAnalyzer:
    """Offline heuristic analyzer for AI-generated text likelihood."""

    AI_TRANSITION_PHRASES = (
        "首先", "其次", "最后", "综上所述", "总而言之", "总的来说", "需要注意的是",
        "in conclusion", "overall", "moreover", "furthermore", "in addition",
        "firstly", "secondly", "finally", "it is important to note",
    )
    AI_SAFETY_PHRASES = (
        "作为一个ai", "我无法", "我不能", "我不具备", "建议咨询专业人士",
        "as an ai", "i cannot", "i'm unable", "consult a professional",
    )

    WEIGHT_REPETITION = 0.28
    WEIGHT_SENTENCE_UNIFORMITY = 0.24
    WEIGHT_TEMPLATE_PHRASE = 0.2
    WEIGHT_PUNCTUATION_REGULARITY = 0.14
    WEIGHT_SAFETY_STYLE = 0.14

    def analyze_text(self, text: str) -> Dict[str, object]:
        normalized_text = self._normalize_text(text)
        if len(normalized_text) < 50:
            return {
                "score": 0,
                "conclusion": "文本长度过短，无法进行可靠判断。",
                "patterns": [],
            }

        sentence_list = self._split_sentences(normalized_text)
        token_list = self._tokenize(normalized_text)

        repetition_score, repetition_detail = self._repetition_feature(token_list)
        sentence_uniformity_score, sentence_uniformity_detail = self._sentence_uniformity_feature(sentence_list)
        template_score, template_detail = self._template_phrase_feature(normalized_text)
        punctuation_score, punctuation_detail = self._punctuation_feature(normalized_text, sentence_list)
        safety_score, safety_detail = self._safety_phrase_feature(normalized_text)

        weighted_score = (
            repetition_score * self.WEIGHT_REPETITION
            + sentence_uniformity_score * self.WEIGHT_SENTENCE_UNIFORMITY
            + template_score * self.WEIGHT_TEMPLATE_PHRASE
            + punctuation_score * self.WEIGHT_PUNCTUATION_REGULARITY
            + safety_score * self.WEIGHT_SAFETY_STYLE
        )
        ai_score = max(0, min(100, round(weighted_score * 100)))

        detected_patterns = self._build_patterns(
            repetition_score,
            repetition_detail,
            sentence_uniformity_score,
            sentence_uniformity_detail,
            template_score,
            template_detail,
            punctuation_score,
            punctuation_detail,
            safety_score,
            safety_detail,
        )

        if ai_score >= 70:
            conclusion = "文本呈现较强的AI生成特征，建议结合上下文进一步复核。"
        elif ai_score >= 40:
            conclusion = "文本存在一定AI生成特征，结论不确定，建议人工复核。"
        else:
            conclusion = "文本更接近人工写作风格，AI生成特征较弱。"

        return {
            "score": ai_score,
            "conclusion": conclusion,
            "patterns": detected_patterns,
        }

    def _normalize_text(self, text: str) -> str:
        normalized_text = (text or "").replace("\r\n", "\n").replace("\r", "\n")
        normalized_text = re.sub(r"\s+", " ", normalized_text)
        return normalized_text.strip()

    def _split_sentences(self, text: str) -> List[str]:
        sentence_candidates = re.split(r"[。！？!?\.]+", text)
        sentence_list = [sentence.strip() for sentence in sentence_candidates if sentence.strip()]
        return sentence_list

    def _tokenize(self, text: str) -> List[str]:
        english_word_tokens = [token.lower() for token in re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", text)]
        chinese_char_tokens = re.findall(r"[\u4e00-\u9fff]", text)
        return english_word_tokens + chinese_char_tokens

    def _repetition_feature(self, tokens: List[str]) -> Tuple[float, str]:
        if len(tokens) < 25:
            return 0.0, "词元数量不足，重复模式贡献较低。"

        trigram_list = [tuple(tokens[index:index + 3]) for index in range(len(tokens) - 2)]
        trigram_counter = Counter(trigram_list)
        repeated_trigram_count = sum(count - 1 for count in trigram_counter.values() if count > 1)
        repetition_ratio = repeated_trigram_count / max(1, len(trigram_list))

        # 0.08 以上视为明显重复，映射到 [0,1]
        repetition_score = min(1.0, repetition_ratio / 0.08)
        detail = f"重复三元组占比约为 {repetition_ratio:.2%}。"
        return repetition_score, detail

    def _sentence_uniformity_feature(self, sentences: List[str]) -> Tuple[float, str]:
        if len(sentences) < 3:
            return 0.0, "句子数量不足，句长一致性贡献较低。"

        sentence_lengths = [len(sentence) for sentence in sentences]
        average_length = sum(sentence_lengths) / len(sentence_lengths)
        variance = sum((length - average_length) ** 2 for length in sentence_lengths) / len(sentence_lengths)
        std_deviation = math.sqrt(variance)
        variation_ratio = std_deviation / max(1.0, average_length)

        # 变化率越低越像模板化生成
        sentence_uniformity_score = max(0.0, min(1.0, (0.5 - variation_ratio) / 0.5))
        detail = f"句长变化率约为 {variation_ratio:.2f}。"
        return sentence_uniformity_score, detail

    def _template_phrase_feature(self, text: str) -> Tuple[float, str]:
        lower_text = text.lower()
        matched_phrases = [phrase for phrase in self.AI_TRANSITION_PHRASES if phrase in lower_text]
        phrase_density = len(matched_phrases) / max(1, len(self._split_sentences(text)))
        template_score = min(1.0, phrase_density / 0.8)

        if matched_phrases:
            matched_preview = "、".join(matched_phrases[:4])
            detail = f"检测到模板化过渡短语：{matched_preview}。"
        else:
            detail = "未检测到明显模板化过渡短语。"
        return template_score, detail

    def _punctuation_feature(self, text: str, sentences: List[str]) -> Tuple[float, str]:
        if not sentences:
            return 0.0, "缺少句子结构，标点模式贡献较低。"

        punctuation_count = len(re.findall(r"[，。！？,.!?;；:：]", text))
        punctuation_density = punctuation_count / max(1, len(text))
        sentence_lengths = [len(sentence) for sentence in sentences]
        if not sentence_lengths:
            return 0.0, "缺少句子长度数据，标点模式贡献较低。"

        average_sentence_length = sum(sentence_lengths) / len(sentence_lengths)

        # 过于稳定的标点密度 + 平均句长接近模板区间（20-45）会提高得分
        template_length_score = 1.0 if 20 <= average_sentence_length <= 45 else 0.35
        density_score = min(1.0, punctuation_density / 0.08)
        punctuation_score = min(1.0, (template_length_score * 0.5 + density_score * 0.5))
        detail = f"标点密度约为 {punctuation_density:.2%}，平均句长约为 {average_sentence_length:.1f}。"
        return punctuation_score, detail

    def _safety_phrase_feature(self, text: str) -> Tuple[float, str]:
        lower_text = text.lower()
        matched_safety_phrases = [phrase for phrase in self.AI_SAFETY_PHRASES if phrase in lower_text]
        if not matched_safety_phrases:
            return 0.0, "未检测到AI常见免责声明措辞。"

        score = min(1.0, len(matched_safety_phrases) / 2)
        detail = f"检测到常见免责声明措辞：{'、'.join(matched_safety_phrases)}。"
        return score, detail

    def _build_patterns(
        self,
        repetition_score: float,
        repetition_detail: str,
        sentence_uniformity_score: float,
        sentence_uniformity_detail: str,
        template_score: float,
        template_detail: str,
        punctuation_score: float,
        punctuation_detail: str,
        safety_score: float,
        safety_detail: str,
    ) -> List[Dict[str, str]]:
        pattern_candidates = [
            ("重复表达模式", repetition_score, repetition_detail),
            ("句式均匀度偏高", sentence_uniformity_score, sentence_uniformity_detail),
            ("模板化过渡短语", template_score, template_detail),
            ("标点与句长规则化", punctuation_score, punctuation_detail),
            ("免责声明措辞", safety_score, safety_detail),
        ]

        patterns: List[Dict[str, str]] = []
        for pattern_name, pattern_score, detail in pattern_candidates:
            if pattern_score < 0.25:
                continue
            patterns.append(
                {
                    "pattern": pattern_name,
                    "description": detail,
                    "confidence": self._confidence_label(pattern_score),
                }
            )

        patterns.sort(
            key=lambda pattern_item: {"High": 3, "Medium": 2, "Low": 1}[pattern_item["confidence"]],
            reverse=True,
        )
        return patterns

    def _confidence_label(self, score: float) -> str:
        if score >= 0.7:
            return "High"
        if score >= 0.45:
            return "Medium"
        return "Low"
