# Profile assets

- `avatar/original.png` is the original anonymous illustration.
- `avatar/pixel.png` is the pixel rendition of the same illustration. The particle generator samples this file without modifying it.
- `terminal/profile.svg` is the current README graphic. It uses declarative SVG animations to move the dots between five shapes in a 25-second loop. “Live” describes the visual, not account activity or live data.
- `terminal/*.png` and `terminal/*.gif` are retained from earlier profile experiments; they are not required by the current README.

To regenerate the SVG, install `scripts/requirements.txt`, install Inkscape, and run `python scripts/generate_particles.py` from the repository root. It also writes five target previews to the system temporary directory. The previous `scripts/render_profile.py` produces the earlier PNG/GIF experiments and is retained for reference; it is not the SVG generator and can overwrite `avatar/pixel.png` if run.

The Python icon silhouette in the generator is adapted from [Simple Icons](https://simpleicons.org/) (CC0-1.0). The original avatar and its pixel version remain available in `avatar/`.
