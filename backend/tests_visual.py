# -*- coding: utf-8 -*-
"""Visual formatting checks on the smoke test DOCX."""

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

d = Document("outputs/smoke_test_affidavit.docx")
P = d.paragraphs

# DEPONENT (verification) right aligned
dep = [p for p in P if p.text.strip() == "DEPONENT"]
assert len(dep) == 1
assert dep[0].alignment == WD_ALIGN_PARAGRAPH.RIGHT
assert all(r.bold for r in dep[0].runs)
print("Verification DEPONENT right-aligned bold OK")

# Jurat lines left aligned
jur = next(p for p in P if p.text.strip().startswith("Solemnly affirmed at"))
assert jur.alignment == WD_ALIGN_PARAGRAPH.LEFT
print("Jurat left-aligned OK")

# Margins + font
s = d.sections[0]
assert s.left_margin.inches == 1.0 and s.right_margin.inches == 1.0
assert s.top_margin.inches == 1.0 and s.bottom_margin.inches == 1.0
st = d.styles["Normal"]
assert st.font.name == "Times New Roman" and st.font.size.pt == 12
print("1-inch margins + TNR 12 OK")

# Exhibit bold in body
ex = [p for p in P if "EXHIBIT" in p.text]
assert ex and any(r.bold and "EXHIBIT" in r.text for r in ex[0].runs)
print("Exhibit bold OK:", ex[0].text)

# Page break before PRAYER exists
prayer_index = next(i for i, p in enumerate(P) if p.text.strip() == "PRAYER")
prev_xml = P[prayer_index - 1]._p.xml
print("Page break present:", "page" in prev_xml and "w:br" in prev_xml)

# Tab stops: RIGHT at 6.5 inches (5943600 EMU)
cause = next(p for p in P if p.text.strip().startswith("Sunrise Housing"))
beforeme = next(p for p in P if p.text.strip().startswith("Before Me"))
for name, p in [("cause title", cause), ("before me", beforeme)]:
    ts = p.paragraph_format.tab_stops[0]
    assert int(ts.alignment) == 2, name  # 2 = WD_TAB_ALIGNMENT.RIGHT
    assert ts.position == 5943600, name
assert not cause.runs[0].bold and not cause.runs[1].bold
assert beforeme.runs[0].text == "Before Me" and not beforeme.runs[0].bold
assert beforeme.runs[1].text == "\tDEPONENT" and beforeme.runs[1].bold
print("Tab stops (RIGHT @ 6.5in) + Before Me/DEPONENT runs OK")

print("ALL REMAINING VISUAL CHECKS PASSED")
