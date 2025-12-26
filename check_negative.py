import re
from pathlib import Path
from collections import defaultdict
from typing import List, Tuple

from story_weaver import RandomTextGenerator

# assume RandomTextGenerator is already defined / imported in the same module
# from your_module import RandomTextGenerator

def _word_count_in_lines(token: str, lines: List[str]) -> int:
    """Count occurrences of token as a whole word in given lines."""
    pattern = re.compile(rf"\b{re.escape(token)}\b", flags=re.IGNORECASE)
    return sum(1 for line in lines if pattern.search(line))

def analyze_template_for_negative_only_options(
    generator: RandomTextGenerator,
    template_path: str,
    positive_file: str,
    negative_file: str,
    min_neg_occurrences: int = 1
) -> List[Tuple[str, str, int, int]]:
    """
    Analyze each bracket-group in template_path and return list of options that:
      - appear at least `min_neg_occurrences` times in negative_file
      - appear 0 times in positive_file

    Returns list of tuples: (group_text, option, pos_count, neg_count)
    """
    tpath = Path(template_path)
    content = tpath.read_text(encoding="utf-8")

    pos_lines = Path(positive_file).read_text(encoding="utf-8").splitlines()
    neg_lines = Path(negative_file).read_text(encoding="utf-8").splitlines()

    # find all bracket groups and their spans so we can substitute just one occurrence at a time
    bracket_re = re.compile(r"\[([^\]]+)\]")
    matches = list(bracket_re.finditer(content))

    results = []

    for idx, m in enumerate(matches):
        group_text = m.group(0)          # e.g., "[pen || eraser]"
        group_inner = m.group(1)         # e.g., "pen || eraser"
        options = [opt.strip() for opt in group_inner.split("||")]

        for opt in options:
            # build a variant content where only this specific bracket occurrence is replaced by 'opt'
            start, end = m.span()
            variant = content[:start] + opt + content[end:]

            # pass the variant line through your generator expansion logic to resolve other references and @sections@
            # we use _expand_inline_and_brackets which expects a single line and a file path (so inline @sections@ are read)
            # if your class exposes a public method for this, prefer that. This call relies on internals but reuses your logic.
            expanded = generator._expand_inline_and_brackets(variant, tpath).strip()

            # now count occurrences of the option token in pos/neg example outputs
            pos_count = _word_count_in_lines(opt, pos_lines)
            neg_count = _word_count_in_lines(opt, neg_lines)

            # Optionally: if you prefer to check presence in the expanded output itself,
            # you could also compare expanded against example lines, but the files likely contain many variants.

            if neg_count >= min_neg_occurrences and pos_count == 0:
                results.append((group_text, opt, pos_count, neg_count))

    return results

# ---------------- Example usage ----------------

def generate_strings(temp_txt_path, txt_dirs, count=100):
    generator = RandomTextGenerator(base_dir="files")  # use same base_dir you normally use
    results = set()
    for _ in range(count):
        generated, _ = generator.get_random_line(temp_txt_path) 
        results.add(generated)
    positive_outputs = [x for x in Path(txt_dirs).glob("**/*.txt") if 'positive' in x.name]
    negative_outputs = [x for x in Path(txt_dirs).glob("**/*.txt") if 'negative' in x.name]
    # breakpoint()
    for test_str in results:
        is_positive = any( test_str in pos.read_text(encoding="utf-8") for pos in positive_outputs)
        is_negative = any( test_str in neg.read_text(encoding="utf-8") for neg in negative_outputs)
        if is_positive or is_negative:
            print(f"Generated: {test_str}  → Positive: {is_positive}  Negative: {is_negative}")
    return results

if __name__ == "__main__":
    # adjust these paths to your environment
    template_file = r"C:\Work\OneDrive - Creative Arts Education Society\Desktop\rarely\G1\to_video\wan3\6969induced_boy\start.txt"    # file that contains "[pen || eraser]" etc and inline @sections@
    txt_dir = r"C:\Work\OneDrive - Creative Arts Education Society\Desktop\rarely\G1\to_video\wan3"     # file with many positive outputs (one per line)
    # negative_txt_dir = r"C:\Work\OneDrive - Creative Arts Education Society\Desktop\rarely\G1\to_video\wan3"    # directory with many negative outputs (one per line)
    # generate_strings(template_file, txt_dir, count=20)
    generate_strings(template_file, txt_dir, count=2000)

    # res = analyze_template_for_negative_only_options(
    #     generator,
    #     template_file,
    #     positive_file,
    #     negative_file,
    #     min_neg_occurrences=1
    # )

    # if not res:
    #     print("No options found that are exclusively negative (by these files).")
    # else:
    #     print("Options always (in your data) causing negative responses:")
    #     for group, opt, pos_count, neg_count in res:
    #         print(f"Group: {group}  → Option: '{opt}'  (pos_count={pos_count}, neg_count={neg_count})")
