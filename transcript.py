from __future__ import annotations
from typing import Any
import nltk
from pytube import Caption
import re
from summarizer import Summarizer
import html

class Transcript:
    def __init__(self, text: str, title: str):
        self.text: str = text
        self.title: str = title
    
    @staticmethod
    def _estimate_token_count(to_estimate: str | list[str | dict[str, Any]], key: str = 'sentence') -> int:
        if not to_estimate:
            return 0
        elif isinstance(to_estimate, str):
            text = to_estimate
        elif isinstance(to_estimate, list):
            if isinstance(to_estimate[0], str):
                text = ' '.join(to_estimate)
            elif isinstance(to_estimate[0], dict):
                text = ' '.join([e[key] for e in to_estimate])
            else:
                raise ValueError('Must provide either a str, or list of strs or dicts.')
        else:
            raise ValueError('Must provide either a str, or list of strs or dicts.')
        return -(len(text) // -4)
    
    def _get_extractive_summary(self, middle_sentences: list[str], middle_token_count: int) -> str:
        summarizer = Summarizer()
        title_words = summarizer.parser.remove_punctations(self.title)
        title_words = summarizer.parser.words(self.title)
        (keywords, word_count) = summarizer.parser.get_keywords(' '.join(middle_sentences))

        top_keywords = summarizer.get_top_keywords(keywords[:10], word_count)

        result = summarizer._compute_score(middle_sentences, title_words, top_keywords)
        result = list(reversed(summarizer.sort_score(result)))
        
        truncated_result = list()
        while self._estimate_token_count(truncated_result) < middle_token_count and result:
            truncated_result.append(result.pop())

        truncated_result = summarizer.sort_sentences(truncated_result)
        return ' '.join([e['sentence'] for e in truncated_result])
    
    def get_truncated_text(self, max_token_count: int = 2048, num_front_sentences: int = 5, num_back_sentences: int = 5) -> str:
        estimated_token_count = self._estimate_token_count(self.text)
        if estimated_token_count <= max_token_count:
            return self.text, False
        
        nltk.download('punkt', quiet=True)
        sentences = nltk.tokenize.sent_tokenize(self.text)
        front_text = ' '.join(sentences[:num_front_sentences])
        middle_sentences = sentences[num_front_sentences:-num_back_sentences]
        back_text = ' '.join(sentences[-num_back_sentences:])
        
        direct_token_count = self._estimate_token_count(front_text) + self._estimate_token_count(back_text)
        middle_token_count = max_token_count - direct_token_count
        
        extractive_summary = self._get_extractive_summary(middle_sentences, middle_token_count)
        
        return ' '.join([front_text, extractive_summary, back_text]), True
    
    @staticmethod
    def from_whisper_result(result: dict[str, Any], title: str) -> Transcript:
        return Transcript(result['text'], title)
    
    @staticmethod
    def from_yt_captions(captions: Caption, title: str) -> Transcript:
        events = captions.json_captions['events']
        text = ''
        back_space = True
        
        for event in events:
            # Skip over any events without segments
            if 'segs' not in event.keys():
                continue
            
            for segment in event['segs']:
                seg_text = segment['utf8']
                # Unescape html special characters
                seg_text = html.unescape(seg_text)
                
                # Fix spaces, either space at end of last segment, or front of this segment.
                seg_front_space = seg_text[0] == ' '
                if back_space and seg_front_space:
                    seg_text = seg_text[1:]
                elif not back_space and not seg_front_space:
                    seg_text = ' ' + seg_text
                back_space = seg_text[-1] == ' '
                
                # Remove any newline characters in the middle of a segment.
                seg_text = re.sub(r'(?<!^)\n(?!$)', ' ', seg_text)
                
                # Fix any double spaces
                seg_text = re.sub(r'\s\s+', ' ', seg_text)

                text += seg_text
        return Transcript(text, title)