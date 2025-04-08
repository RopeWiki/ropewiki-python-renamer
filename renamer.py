#!/usr/bin/env python3
import mwclient
from pprint import pprint
import re
from typing import List, Tuple, Dict, Set
import os
import sys
import logging

logging.basicConfig(level=logging.INFO)

# Uncomment to debug API HTTP calls.
# import http.client
# http.client.HTTPConnection.debuglevel = 1


class Renamer:
    def __init__(
        self, site_url: str, username: str, password: str, old_name: str, new_name: str
    ):
        """
        Initialize the Renamer with MediaWiki site credentials and the old/new names.
        """
        self.site = mwclient.Site(site_url, path="/")
        self.site.login(username, password)
        self.old_name = old_name
        self.new_name = new_name

    def query_ask(self, query: str) -> Set[str]:
        """
        Perform a MediaWiki API query and return the results as a set of strings.
        """
        return set(answer["fulltext"] for answer in self.site.ask(query))

    def rename_conditions(self, conditions: Set[str]) -> List[Tuple[str, str]]:
        """
        Rename conditions in the format:
        Conditions:Davis Creek Canyon-20241009060850
        """
        return [
            (
                c,
                c.replace(
                    f"Conditions:{self.old_name}-", f"Conditions:{self.new_name}-"
                ),
            )
            for c in conditions
        ]

    def rename_ratings(self, ratings: Set[str]) -> List[Tuple[str, str]]:
        """
        Rename ratings in the format:
        Votes:Davis Creek Canyon/Ames
        """
        return [
            (r, r.replace(f"Votes:{self.old_name}/", f"Votes:{self.new_name}/"))
            for r in ratings
        ]

    def rename_lists(self, lists: Set[str]) -> List[Tuple[str, str]]:
        """
        Rename lists in the format:
        Lists:Fil/Davis Creek Canyon
        """
        regex = f"^(Lists:.+)/{self.old_name}"
        return [(l, re.sub(regex, rf"\1/{self.new_name}", l)) for l in lists]

    def rename_references(self, references: Set[str]) -> List[Tuple[str, str]]:
        """
        Rename references in the format:
        References:Davis Creek Canyon-20160624185152
        """
        return [
            (
                r,
                r.replace(
                    f"References:{self.old_name}-", f"References:{self.new_name}-"
                ),
            )
            for r in references
        ]

    def rename_incidents(self, incidents: Set[str]) -> List[Tuple[str, str]]:
        """
        Rename incidents in the format:
        Incidents:Broken hand in Davis Creek Canyon (sometimes date here)
        """
        return [
            (i, i.replace(f"in {self.old_name}", f"in {self.new_name}"))
            for i in incidents
        ]

    def simple_replace(self, input: Set[str]) -> List[Tuple[str, str]]:
        """
        Perform a simple replacement of the old name with the new name.
        """
        i = input.pop()
        return [(i, i.replace(self.old_name, self.new_name))]

    def rename(self, old_page_name: str, new_page_name: str) -> None:
        """
        Rename a MediaWiki page from old_page_name to new_page_name.
        """
        if old_page_name == new_page_name:
            print(f"❓ {old_page_name} already done?")
            return

        page = self.site.pages[old_page_name]
        page.move(new_page_name, reason="Renaming")

    def fixup_location(self, page_names: List[Tuple[str, str]], field: str) -> None:
        """
        Fetch a given page and update the location as set in the provided "field".
        """
        for old_page_name, new_page_name in page_names:
            print(f"➡️ Fixing-up {field} field on {new_page_name}")
            response = self.site.api(
                "parse", page=new_page_name, format="json", prop="wikitext"
            )
            text = response["parse"]["wikitext"]["*"]
            updated_text = text.replace(
                f"|{field}={self.old_name}\n", f"|{field}={self.new_name}\n"
            )

            if text == updated_text:
                print(f"No change! {new_page_name}")
                return

            page = self.site.pages[new_page_name]
            summary = f"Updated {field} to {self.new_name}"
            page.save(updated_text, summary=summary)

    def do_the_work(self, renames: Dict[str, List[Tuple[str, str]]]) -> None:
        """
        Perform the actual renaming work.
        """
        for page_type, page_names in renames.items():
            for old_page_name, new_page_name in page_names:
                print(f"➡️ {old_page_name} --> {new_page_name}")
                self.rename(old_page_name, new_page_name)

            if page_type in ["conditions", "lists", "references", "incidents"]:
                self.fixup_location(page_names, "Location")

            if page_type == "ratings":
                self.fixup_location(page_names, "Place")


if __name__ == "__main__":
    # Load MediaWiki credentials from environment variables.
    site_url, username, password = (
        os.getenv(var)
        for var in ["MEDIAWIKI_SITE_URL", "MEDIAWIKI_USERNAME", "MEDIAWIKI_PASSWORD"]
    )

    if not all([site_url, username, password]):
        sys.exit(
            "Error: Ensure MEDIAWIKI_SITE_URL, MEDIAWIKI_USERNAME, and MEDIAWIKI_PASSWORD are all set."
        )

    # Parse command-line arguments for old and new names.
    if len(sys.argv) != 3:
        sys.exit("Usage: renamer.py <old_name> <new_name>")

    old_name = sys.argv[1]
    new_name = sys.argv[2]

    # Initialize the Renamer object.
    renamer = Renamer(site_url, username, password, old_name, new_name)

    if not renamer.query_ask(f"[[{old_name}]]"):
        print(f'⚠️ "{old_name}" doesn\'t seem to exist!')
        sys.exit(1)

    # Prepare the renames dictionary.
    renames: Dict[str, List[Tuple[str, str]]] = {}

    renames["principle"] = renamer.simple_replace(renamer.query_ask(f"[[{old_name}]]"))

    # renames["kml"] = renamer.simple_replace(renamer.query_ask(f"[[File:{old_name}.kml]]"))

    renames["conditions"] = renamer.rename_conditions(
        renamer.query_ask(
            f"[[Category:Conditions]][[Has condition location::{old_name}]]"
        )
    )
    renames["ratings"] = renamer.rename_ratings(
        renamer.query_ask(
            f"[[Category:Page ratings]][[Has page rating page::{old_name}]]"
        )
    )
    renames["lists"] = renamer.rename_lists(
        renamer.query_ask(f"[[Category:Lists]][[Has location::{old_name}]]")
    )
    renames["incidents"] = renamer.rename_incidents(
        renamer.query_ask(
            f"[[Category:Incidents]][[Has incident location::{old_name}]]"
        )
    )
    renames["references"] = renamer.rename_references(
        renamer.query_ask(
            f"[[Category:References]][[Has condition location::{old_name}]]"
        )
    )

    # Print and execute the renaming tasks.
    pprint(renames)
    # renamer.do_the_work(renames)
