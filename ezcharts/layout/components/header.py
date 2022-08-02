"""Get default header layouts."""
from typing import Callable, NamedTuple, Union

from dominate.svg import svg
from dominate.tags import a, div, header, img, li, ul


def report_header_link(
    title: str,
    href: str,
    list_item_classes="nav-item",
    list_item_link_classes="nav-link text-white"
) -> li:
    """
    Generate a header nav link component with
    labs-bootstrap styling by default, compatible with
    report_header.

    :returns: The li that contains the nav link.
    """
    _item = li(className=list_item_classes)
    with _item:
        a(title, href=href, className=list_item_link_classes)
    return _item


class IHeaderReturn(NamedTuple):
    """Specifies the return types for report_header."""
    main: header
    links: ul


def report_header(
    logo: Union[
        str,
        Callable[[], svg],
        Callable[[], img]
    ] = "./assets/logo.svg",
    header_height: int = 75,
    header_classes: str = (
        "fixed-top d-flex align-items-center flex-wrap "
        "justify-content-center bg-dark"
    ),
    container_classes: str = (
        "container px-0 d-flex flex-wrap "
        "justify-content-center align-items-center py-3"
    ),
    logo_link_classes: str = (
        "d-flex align-items-center pe-5 mb-md-0 me-md-auto "
        "text-decoration-none"
    ),
    list_class="nav nav-pills",
) -> IHeaderReturn:
    """
    Generate a header component with labs-bootstrap
    styling and fixed positioning by default. A spacer div
    is created above the header to pad the contents below.
    It contains a logo and an array for nav links.

    :returns: The header element and the ul that
        contains the nav links.
    """
    _spacer = div(
        className="d-flex", style=f"margin-top: {header_height}px;")
    _header = header(
        className=header_classes, style=f"height: {header_height}px;")
    _spacer += _header
    with _header:
        with div(className=container_classes):
            with a(href="/", className=logo_link_classes):
                if isinstance(logo, str):
                    img(src=logo, width="25px", alt="EPI2ME Labs Logo")
                else:
                    logo()
            _links = ul(className=list_class, __pretty=False)
    return IHeaderReturn(_header, _links)
