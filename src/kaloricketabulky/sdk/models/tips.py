"""Diet analysis tips."""

from kaloricketabulky.sdk.models.common import ApiModel


class Tip(ApiModel):
    """A single praise/warning tip from the analysis endpoint (text is Czech)."""

    key: str
    title: str | None = None
    text: str | None = None
    advice: str | None = None
    icon: str | None = None
    indicator: int | None = None
    order: int | None = None
