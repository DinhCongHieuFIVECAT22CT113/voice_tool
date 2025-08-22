"""
File này chứa các rule (quy tắc) xử lý cắt audio, hậu kiểm, điều chỉnh ngắt nghỉ cho dự án voice_tools v3.
Có thể mở rộng thêm các rule AI hoặc rule thủ công.
"""

import re
from typing import List, Tuple

# Rule: Tìm vị trí dấu câu trong văn bản
PUNCTUATION_REGEX = r'[.!?…\n]'  # Có thể mở rộng thêm dấu câu tiếng Việt

def find_punctuation_indices(text: str) -> List[int]:
    """Trả về danh sách chỉ số (index) các dấu câu trong text."""
    return [m.end() for m in re.finditer(PUNCTUATION_REGEX, text)]

# Rule: Hậu kiểm điểm cắt (có thể cộng/trừ thêm ms nếu cần)
def adjust_cut_points(points: List[int], min_gap: int = 200) -> List[int]:
    """Loại bỏ các điểm cắt quá gần nhau (< min_gap ms)."""
    if not points:
        return []
    result = [points[0]]
    for p in points[1:]:
        if p - result[-1] >= min_gap:
            result.append(p)
    return result

# Có thể bổ sung các rule khác: random frame, thêm im lặng, ...
