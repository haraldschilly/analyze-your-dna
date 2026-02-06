from typing import TypedDict
from typing_extensions import NotRequired

class VariantInfo(TypedDict):
    """
    Type definition for variant information.

    Attributes:
        status (str): Short status descriptor (e.g., 'normal', 'carrier', 'affected')
        desc (str): Detailed user-facing description
        magnitude (int): Impact score (0-5), where 0 is neutral and 5 is critical
    """

    status: str
    desc: str
    magnitude: int


class SnpInfo(TypedDict):
    """
    Type definition for SNP entry.

    Attributes:
        gene (str): Gene symbol
        category (str): Health category
        variants (dict[str, VariantInfo]): Map of genotype (e.g., 'AA') to variant info
        note (NotRequired[str]): Optional scientific context or mechanism details
    """

    gene: str
    category: str
    variants: dict[str, VariantInfo]
    note: NotRequired[str]


# Type alias for the database structure
SnpDatabase = dict[str, SnpInfo]
