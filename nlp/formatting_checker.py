"""
formatting_checker.py
----------------------
Checks resume formatting risks that can affect ATS parsing.
"""

from dataclasses import dataclass, field


PENALTIES = {
    "likely_scanned_image": 1.0,
    "used_text_boxes": 0.35,
    "used_tables": 0.25,
    "multi_column_layout": 0.20,
    "used_headers_footers": 0.10,
}


@dataclass
class FormattingCheckResult:

    formatting_score: float = 1.0

    issues: list = field(
        default_factory=list
    )


def check_formatting(extraction_result):

    result = FormattingCheckResult()

    penalty_total = 0.0

    for flag_name, weight in PENALTIES.items():

        if getattr(
            extraction_result,
            flag_name,
            False
        ):

            penalty_total += weight

            result.issues.append(
                flag_name
            )

    result.formatting_score = round(
        max(
            0.0,
            1.0 - penalty_total
        ),
        4
    )

    return result