from dataclasses import dataclass
from typing import List, Union
from rapidfuzz import fuzz
import bs4
import re

from ebooklib import epub

from highlights_prettifier.preprocess import default_preprocess


@dataclass
class TocTitle:
    element: Union[epub.Link, epub.Section]
    level: int


def fix_titles(book, soup: bs4.BeautifulSoup) -> bs4.BeautifulSoup:
    dfs_toc_titles = dfs_tree_to_list(book.toc, level=1)

    bfs_toc_titles = dfs_to_bfs(dfs_toc_titles)
    dfs_html_titles: List[bs4.element.Tag] = soup.find_all(re.compile("h[1-6]"))
    # Sort the items by heading level
    bfs_html_titles: List[bs4.element.Tag] = sorted(
        dfs_html_titles, key=get_heading_level
    )

    missing_toc_titles, extra_html_titles = get_not_matching_titles(
        toc_titles=bfs_toc_titles, html_titles=bfs_html_titles
    )
    fixed_soup = add_missing_toc_titles(
        toc_titles=missing_toc_titles, soup=soup
    )

    return fixed_soup


def dfs_tree_to_list(tree, level=0) -> List[TocTitle]:
    result = []
    for item in tree:
        if isinstance(item, tuple):
            # Split section and childs
            section, children = item
            result.append(TocTitle(element=section, level=level))
            # Recursively call the DFS function on the sub-tree (branch)
            if isinstance(children, list):
                result.extend(dfs_tree_to_list(children, level + 1))
            else:
                raise ValueError("Unexpected content format")
        else:
            # Append the current item (leaf) along with its level
            result.append(TocTitle(element=item, level=level))
    return result


def dfs_to_bfs(dfs_toc_titles: List[TocTitle]) -> List[TocTitle]:
    bfs_result = []
    level_map = {}

    for toc_title in dfs_toc_titles:
        if toc_title.level not in level_map:
            level_map[toc_title.level] = []
        level_map[toc_title.level].append(toc_title)

    max_level = max(level_map.keys())

    for level in range(max_level + 1):
        if level in level_map:
            bfs_result.extend([toc_title for toc_title in level_map[level]])

    return bfs_result


def is_match(toc_title: TocTitle, html_title: bs4.element.Tag):
    # Extract level from HTML title
    html_level = (
        int(html_title.name[1:])
        if html_title.name and html_title.name.startswith("h")
        else 0
    )

    if toc_title.level != html_level:
        return False
    if (
        toc_title.element.href is not None
        and toc_title.element.href == html_title.attrs.get("id")
    ):
        return True

    # TODO Improve title matching algorithm. It's hacky with 90ish
    toc_text = toc_title.element.title
    html_text = html_title.get_text()
    if fuzz.partial_ratio_alignment(
        toc_text, html_text, score_cutoff=90, processor=default_preprocess
    ):
        return True

    return False


# TODO Assuming first level match but it should be corrected previously
def get_not_matching_titles(
    toc_titles: List[TocTitle], html_titles=List[bs4.element.Tag]
):
    not_matching_toc_titles = []
    not_matching_html_titles = []
    toc_idx = 0
    html_idx = 0

    while toc_idx < len(toc_titles) and html_idx < len(html_titles):
        toc_title = toc_titles[toc_idx]
        html_title = html_titles[html_idx]

        if toc_title.level < int(html_title.name[1:]):
            not_matching_toc_titles.append(toc_title)
            toc_idx += 1
        elif toc_title.level > int(html_title.name[1:]):
            not_matching_html_titles.append(html_title)
            html_idx += 1
        else:
            # Levels match, compare content
            if is_match(toc_title, html_title):
                # Match, advance
                toc_idx += 1
                html_idx += 1
            else:
                # Check the rest of the HTML titles looking forward
                for i in range(html_idx, len(html_titles)):
                    if is_match(toc_title, html_titles[i]):
                        not_matching_html_titles.extend(html_titles[html_idx:i])
                        html_idx = i
                        break
                else:
                    # Failed to find toc_title
                    not_matching_toc_titles.append(toc_title)
                    toc_idx += 1

    # Add remaining TOC titles if any
    while toc_idx < len(toc_titles):
        not_matching_toc_titles.append(toc_titles[toc_idx])
        toc_idx += 1

    while html_idx < len(html_titles):
        not_matching_html_titles.append(html_titles[html_idx])
        html_idx += 1

    return not_matching_toc_titles, not_matching_html_titles


def add_missing_toc_titles(toc_titles, soup):
    for toc_title in toc_titles:
        new_tag = _crate_title_tag(soup, toc_title)

        html_title = soup.find(id=toc_title.element.href)
        if not html_title:
            partial_href_match = find_partial_href_match(
                soup, toc_title.element.href
            )
            tag_text_match = find_tag_text_match(
                element=partial_href_match, text=toc_title.element.title
            )
            # TODO Insert in the right place with an insertion algorithm
            tag_text_match.insert_after(new_tag)
        else:
            html_title.insert_after(new_tag)

    return soup


def _crate_title_tag(soup, toc_title):
    new_tag = soup.new_tag(name=f"h{toc_title.level}")
    new_tag.string = toc_title.element.title
    return new_tag


def find_partial_href_match(soup, href):
    if "#" in href:
        main_ref = href.split("#")[0]
        html_titles_loose = soup.find(id=main_ref)
        return html_titles_loose


def find_tag_text_match(element: bs4.element.Tag, text: str):
    if tag_matches_text(element, text):
        return element

    # Check next siblings and their childs
    for sibling in element.find_next_siblings():
        sibling_child_match = sibling.find(
            lambda tag: tag_matches_text(tag, text), recursive=True
        )
        if sibling_child_match:
            return sibling_child_match

    # Check parent and its siblings recursively
    parent = element.find_parent()
    if parent:
        # Recurse
        return find_tag_text_match(parent, text)
    # End condition
    return None


def tag_matches_text(tag: bs4.element.Tag, needle_text: str):
    hay_text = tag.get_text()
    result = (
        len(hay_text) > len(needle_text)
        # TODO Consider doing only ratio
        and fuzz.ratio(
            hay_text,
            needle_text,
            score_cutoff=90,
            processor=default_preprocess,
        )
    )
    return result


def find_text_match(element: bs4.element.Tag, text: str, matching_function):
    if matching_function(element, text):
        return element

    # Check next siblings
    for sibling in element.find_next_siblings():
        if matching_function(sibling, text):
            return sibling

    # Check parent and its siblings recursively
    parent = element.find_parent()
    while parent:
        for sibling in parent.find_next_siblings():
            if matching_function(sibling, text):
                return sibling
        parent = parent.find_parent()

    return None


# Define a function to extract heading levels
def get_heading_level(item):
    tag_name = item.name
    if tag_name.startswith("h"):
        return int(tag_name[1:])
    return 0
