# Property photography

Real photos go here, then update the matching `src` in `index.html`.
Find every one with:

    grep -n "PLACEHOLDER IMAGE" index.html

Suggested names (16 images):

    hero.jpg              wide landscape, keep the left third uncluttered
    og-card.jpg           1200x630 social preview
    room-female-single.jpg
    room-female-twin.jpg
    room-female-triple.jpg
    room-male-single.jpg
    room-male-twin.jpg
    room-male-triple.jpg
    about.jpg             4:5 portrait crop
    gallery-01.jpg .. gallery-08.jpg

Keep the `width`/`height` attributes on each `<img>` accurate so the layout
does not shift while images load. Alt text is translated — update it in
`i18n/en.json` and `i18n/tr.json`, not in the HTML.
