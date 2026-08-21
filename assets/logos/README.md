# University logos

All six are in place — every university on the site is a **private (vakıf)** university
whose logo was in the supplied asset pack.

| File | University | Campus |
|---|---|---|
| `gelisim.png`    | İstanbul Gelişim Üniversitesi          | Avcılar |
| `beykent.png`    | Beykent Üniversitesi                   | Beylikdüzü |
| `aydin.png`      | İstanbul Aydın Üniversitesi           | Florya |
| `arel.png`       | İstanbul Arel Üniversitesi            | Tepekent |
| `izu.png`        | İstanbul Sabahattin Zaim Üniversitesi | Halkalı |
| `bahcesehir.png` | Bahçeşehir Üniversitesi (**İstanbul**) | Beşiktaş |

Watch out: the asset pack contains four "Bahçeşehir" files and three of them are the
**Cyprus** campus. The one used here is `Istanbul Bahçeşehir University.png`.

## How these were prepared

Each was cropped to its artwork (the originals carried large, uneven transparent margins,
which would have made them render at visibly different optical sizes), downscaled to a
200px long edge, and saved as a palette PNG where that was smaller without visible loss.
About 700 KB of source → **140 KB** for all six.

Re-run that if you swap a file in. Requirements for a replacement: **transparent**
background, trimmed to the artwork, SVG preferred. Update the extension in the matching
`<img src>` in `index.html` if it isn't `.png`.

If a file is ever missing, the `<img>` removes itself via `onerror` and the card falls back
to a monogram tile (İGÜ, BEY, İAÜ, AREL, İZÜ, BAU) — so there are never broken-image icons.

The logo well is **92×64px**, deliberately wider than tall: several of these marks are
horizontal wordmark lockups (Gelişim's artwork is 2.4:1), and a square well would shrink
those to an illegible strip. See the comment in `css/_universities.css`.

**These are trademarks.** Get permission before publishing them.
