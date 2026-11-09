"""Moodius design system tokens (Phase 1 Summary, approved 20 Oct 2026).

No statues, gold, marble or gradients. Flat Slate grounds, Bone type, one Ember accent.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")

SLATE = (0x1B, 0x1F, 0x24)
GRAPHITE = (0x2A, 0x2F, 0x36)
CHARCOAL = (0x3A, 0x40, 0x49)
BONE = (0xF3, 0xEF, 0xE7)
ASH = (0xB8, 0xB3, 0xA9)
EMBER = (0xC9, 0x74, 0x2E)


def hexc(rgb):
    return "0x%02X%02X%02X" % rgb


DISPLAY = os.path.join(FONTS, "Playfair-SemiBold.ttf")      # covers, claims
DISPLAY_XB = os.path.join(FONTS, "Playfair-ExtraBold.ttf")  # big numerals
QUOTE = os.path.join(FONTS, "Playfair-MediumItalic.ttf")     # pull quotes
BODY = os.path.join(FONTS, "Inter-Regular.otf")
BODY_M = os.path.join(FONTS, "Inter-Medium.otf")
BODY_SB = os.path.join(FONTS, "Inter-SemiBold.otf")

MARGIN = 96          # safe margin on every canvas
COLS = 12            # grid columns
HANDLE = "@moodiusaurelius"
WORDMARK = "MOODIUS"
