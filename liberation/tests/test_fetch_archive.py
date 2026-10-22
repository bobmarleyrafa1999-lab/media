import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import fetch_archive as fa  # noqa: E402


class Licence(unittest.TestCase):
    def test_open_licences_pass(self):
        for name in ["Public domain", "PD-US", "CC0", "CC BY 4.0", "CC-BY-2.0", "No known restrictions on publication"]:
            self.assertEqual(fa.classify_licence(name), "ok", name)

    def test_restricted_licences_fail(self):
        for name in ["CC BY-NC 2.0", "CC BY-ND 4.0", "CC BY-NC-SA 3.0", "Fair use", "All rights reserved", "", None]:
            self.assertEqual(fa.classify_licence(name), "no", name)

    def test_share_alike_needs_flag(self):
        self.assertEqual(fa.classify_licence("CC BY-SA 4.0"), "sa")
        self.assertEqual(fa.classify_licence("CC BY-SA 4.0", allow_sa=True), "ok")

    def test_loc_rights(self):
        self.assertTrue(fa.loc_rights_ok("No known restrictions on publication."))
        self.assertTrue(fa.loc_rights_ok(["No known restrictions on publication."]))
        self.assertFalse(fa.loc_rights_ok("Rights status not evaluated."))
        self.assertFalse(fa.loc_rights_ok("Publication may be restricted."))


class Parsers(unittest.TestCase):
    def test_commons_keeps_only_open(self):
        data = {"query": {"pages": {
            "1": {"title": "File:A.jpg", "imageinfo": [{"thumburl": "https://x/a.jpg", "descriptionurl": "https://c/A",
                  "extmetadata": {"LicenseShortName": {"value": "Public domain"},
                                  "Artist": {"value": "<a href='x'>Warren K. Leffler</a>"},
                                  "DateTimeOriginal": {"value": "1963-08-28"}}}]},
            "2": {"title": "File:B.jpg", "imageinfo": [{"url": "https://x/b.jpg",
                  "extmetadata": {"LicenseShortName": {"value": "CC BY-SA 4.0"}}}]},
            "3": {"title": "File:C.jpg", "imageinfo": [{"url": "https://x/c.jpg",
                  "extmetadata": {"LicenseShortName": {"value": "CC BY-NC 2.0"}}}]},
        }}}
        got = fa.parse_commons(data)
        self.assertEqual([g["title"] for g in got], ["A.jpg"])
        self.assertEqual(got[0]["creator"], "Warren K. Leffler")
        self.assertEqual(len(fa.parse_commons(data, allow_sa=True)), 2)

    def test_openverse(self):
        data = {"results": [
            {"title": "March", "creator": "LoC", "license": "pdm", "url": "https://x/1.jpg", "source": "flickr"},
            {"title": "Kept out", "license": "by-nc", "license_version": "2.0", "url": "https://x/2.jpg"},
            {"title": "By", "license": "by", "license_version": "4.0", "url": "https://x/3.jpg"},
        ]}
        self.assertEqual([g["title"] for g in fa.parse_openverse(data)], ["March", "By"])

    def test_loc_item(self):
        ok = {"item": {"title": "Civil Rights March on Washington, D.C.", "date": "1963-08-28",
                       "contributor_names": ["Leffler, Warren K., photographer"],
                       "rights_advisory": ["No known restrictions on publication."],
                       "image_url": ["https://tile.loc.gov/a.jpg", "https://tile.loc.gov/b.jpg"],
                       "id": "https://www.loc.gov/item/2013648812/"}}
        got = fa.parse_loc_item(ok)
        self.assertEqual(got["image_url"], "https://tile.loc.gov/b.jpg")
        self.assertEqual(got["creator"], "Leffler, Warren K., photographer")
        blocked = {"item": dict(ok["item"], rights_advisory=["Rights status not evaluated."])}
        self.assertIsNone(fa.parse_loc_item(blocked))

    def test_credit_line(self):
        self.assertEqual(fa.credit_line("Warren K. Leffler", "1963", "Library of Congress", "No known restrictions"),
                         "Photo: Warren K. Leffler, 1963 · Library of Congress (No known restrictions)")


if __name__ == "__main__":
    unittest.main()
