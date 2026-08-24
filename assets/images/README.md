# Property photography

Real photographs of the building, supplied by the client and prepared for the
web (EXIF rotation applied, resized, JPEG q80 progressive — q72 for the two
that are displayed full-bleed, where a dark scrim hides the difference).

| file | what it shows | used for |
|---|---|---|
| `room-double-3.jpg` | two beds, desks, TV, mini fridge | **hero** |
| `entrance-lobby.jpg` | entrance and common seating area | About scroll-expand, gallery |
| `room-single-1.jpg`  | one bed, bedside table, wardrobe | Single Room card + rooms page |
| `room-double-1.jpg`  | two beds, TV, bathroom door | Double Room card + slider |
| `room-double-2.jpg`  | two beds and the ensuite shower/basin | slider, gallery |
| `room-double-4.jpg`  | double room from the doorway | slider, gallery |
| `corridor.jpg`       | corridor on the residence floors | gallery |
| `room-doorway.jpg`   | doorway into a room | gallery |
| `og-card.jpg`        | 1200x630 crop of the entrance | social preview |

## Still needed

**Photographs of the triple and quad rooms.** Those two cards are the only
stock images left on the site. A two-bed photograph must not be put on a card
that says three or four students — that is why they were not simply reused.

Also worth having: the **building exterior**. The price poster contains a night
shot with the signage but only at 443x418px with the logo across it.

## Adding more

Drop new files here, then reference them. Photographs for a room type go in the
`PHOTOS` map in `tools/build-rooms-page.py` — a list per room type, and any type
with more than one becomes a slider automatically. Re-run:

    python tools/build-rooms-page.py

Update the matching `alt` text in **both** `i18n/*.json`; the alt values are
translated, not written in the HTML.
