# Profile assets

- `avatar/original.png`: original anonymous illustration on white; used in terminal scenes.
- `avatar/pixel.png`: matching 64-cell pixel illustration, exported at 1024 × 1024; ready for manual GitHub avatar upload.
- `terminal/profile.gif`: desktop five-scene loop, 4.2 seconds per scene.
- `terminal/profile-mobile.gif`: vertically arranged mobile version.
- `terminal/*.png`: static and reduced-motion alternatives.

The terminal is a rendered animation, not a running shell. “live” describes the visual loop, not online presence or live account data. All assets are served from this repository. There are no counters or remote widgets.

To rebuild, install `scripts/requirements.txt`, then run `python scripts/render_profile.py`. Python 3.10+ is required. The script uses DejaVu Sans Mono, which must be installed or available to Pillow. The committed PNG/GIF files require no dependencies to display.

The original illustration was AI-generated from this brief: an original minimalist black-ink anonymous seated abstract figure, hollow round head, thoughtful pose, generous white space, no face, text, logos, or identifying features. The pixel avatar is derived from the same original, rather than a separately generated character.

Only the alias is used in profile content. Repository visibility and account-avatar changes are managed separately in GitHub settings.
