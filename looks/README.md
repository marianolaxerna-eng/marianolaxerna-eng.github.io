# looks/

Colours and fonts of every version of the site, for the desktop apps. No need to parse HTML or CSS.

1. Read `https://marianolaxerna-eng.github.io/looks/index.json`. `main` is the id of the current main page.
2. Read `looks/<path>` for that id (`look.json`).
3. `colors.dark` / `colors.light`: hex values with the keys `bg, text, muted, line, border, accent`
   (v1 and v2 also have `block, title, buttonBg, buttonText, hoverBg, hoverText`). `8bit` has no light mode.
4. `roles.<mode>`: which font family is used for `title`, `ui` and `text`.
5. `fonts[].file` is relative to the folder of that `look.json`.

Versions: `v1`, `v2`, `boca`, `index` (editorial), `8bit`.

## Updating

Edit the site, then run `python looks/build.py`, commit and push. When another version becomes the
main page, change `MAIN` in `build.py` first.
