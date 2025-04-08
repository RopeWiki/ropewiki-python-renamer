#!/usr/bin/env python3
import mwclient
from pprint import pprint
import re
from typing import List, Tuple, Dict, Set
import os

import logging

logging.basicConfig(level=logging.INFO)

# Uncomment to debug API HTTP calls.
# import http.client
# http.client.HTTPConnection.debuglevel = 1


def query_ask(query: str) -> Set[str]:
    return set(answer["fulltext"] for answer in SITE.ask(query))


def rename_conditions(conditions: Set[str]) -> List[Tuple[str, str]]:
    """
    Conditions:Davis Creek Canyon-20241009060850
    """
    return [
        (c, c.replace(f"Conditions:{OLD_NAME}-", f"Conditions:{NEW_NAME}-"))
        for c in conditions
    ]


def rename_ratings(ratings: Set[str]) -> List[Tuple[str, str]]:
    """
    Votes:Davis Creek Canyon/Ames
    """
    return [(r, r.replace(f"Votes:{OLD_NAME}/", f"Votes:{NEW_NAME}/")) for r in ratings]


def rename_lists(lists: Set[str]) -> List[Tuple[str, str]]:
    """
    Lists:Fil/Davis Creek Canyon
    """
    regex = f"^(Lists:.+)/{OLD_NAME}"
    return [(l, re.sub(regex, rf"\1/{NEW_NAME}", l)) for l in lists]


def rename_references(references: Set[str]) -> List[Tuple[str, str]]:
    """
    References:Davis Creek Canyon-20160624185152
    """
    return [
        (r, r.replace(f"References:{OLD_NAME}-", f"References:{NEW_NAME}-"))
        for r in references
    ]


def rename_incidents(incidents: Set[str]) -> List[Tuple[str, str]]:
    """
    Incidents:Broken hand in Davis Creek Canyon (sometimes date here)
    """
    return [(i, i.replace(f"in {OLD_NAME}", f"in {NEW_NAME}")) for i in incidents]


def simple_replace(input: Set[str]) -> List[Tuple[str, str]]:
    i = input.pop()
    return [(i, i.replace(OLD_NAME, NEW_NAME))]


def rename(old_page_name: str, new_page_name: str) -> None:
    if old_page_name == new_page_name:
        print(f"❓ {old_page_name} already done?")
        return

    page = SITE.pages[old_page_name]
    page.move(new_page_name, reason="Renaming")


def fixup_location(page_names: List[Tuple[str, str]], field: str) -> None:
    """
    This fetches a given page, and updates the location as set in the provided "field"
    """
    for old_page_name, new_page_name in page_names:
        print(f"➡️ Fixing-up {field} field on {new_page_name}")
        response = SITE.api("parse", page=new_page_name, format="json", prop="wikitext")
        text = response["parse"]["wikitext"]["*"]
        updated_text = text.replace(f"|{field}={OLD_NAME}\n", f"|{field}={NEW_NAME}\n")

        if text == updated_text:
            print(f"No change! {new_page_name}")
            return

        page = SITE.pages[new_page_name]
        summary = f"Updated {field} to {NEW_NAME}"
        page.save(updated_text, summary=summary)


def do_the_work(renames: Dict[str, List[Tuple[str, str]]]) -> None:
    """
    The actual heavy lifting.
    """
    for page_type, page_names in renames.items():
        for old_page_name, new_page_name in page_names:
            print(f"➡️ {old_page_name} --> {new_page_name}")
            rename(old_page_name, new_page_name)

        if page_type in ["conditions", "lists", "references", "incidents"]:
            fixup_location(page_names, "Location")

        for page_type in ["ratings"]:
            fixup_location(page_names, "Place")


if __name__ == "__main__":

    site_url, username, password = (
        os.getenv(var)
        for var in ["MEDIAWIKI_SITE_URL", "MEDIAWIKI_USERNAME", "MEDIAWIKI_PASSWORD"]
    )

    if not all([site_url, username, password]):
        sys.exit(
            "Error: Ensure MEDIAWIKI_SITE_URL, MEDIAWIKI_USERNAME, and MEDIAWIKI_PASSWORD are all set."
        )

    SITE = mwclient.Site(site_url, path="/")
    SITE.login(username, password)

    OLD_NAME = "Davis Creek Canyon"
    NEW_NAME = "Bob Land"

    pprint(query_ask(f"[[File:{OLD_NAME}]]"))
    import sys
    sys.exit()

    renames: Dict[str, List[Tuple[str, str]]] = {}

    renames["principle"] = simple_replace(query_ask(f"[[{OLD_NAME}]]"))

    # renames["kml"] = simple_replace(query_ask(f"[[File:{OLD_NAME}.kml]]"))

    renames["conditions"] = rename_conditions(
        query_ask(f"[[Category:Conditions]][[Has condition location::{OLD_NAME}]]")
    )
    renames["ratings"] = rename_ratings(
        query_ask(f"[[Category:Page ratings]][[Has page rating page::{OLD_NAME}]]")
    )
    renames["lists"] = rename_lists(
        query_ask(f"[[Category:Lists]][[Has location::{OLD_NAME}]]")
    )
    renames["incidents"] = rename_incidents(
        query_ask(f"[[Category:Incidents]][[Has incident location::{OLD_NAME}]]")
    )
    renames["references"] = rename_references(
        query_ask(f"[[Category:References]][[Has condition location::{OLD_NAME}]]")
    )

    pprint(renames)
    do_the_work(renames)
