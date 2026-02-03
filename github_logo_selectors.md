# GitHub logo: color hex, size, and selectors

## Color hex (for scan / CV)

| Context | Hex | Notes |
|--------|-----|--------|
| **Octocat on light bg (e.g. Render login)** | `#000000` | Black; image description confirms |
| **GitHub brand dark gray** | `#232925` | Gray 5, brand.github.com |
| **GitHub brand black** | `#101411` | Gray 6, Process Black |
| **GitHub green (accent)** | `#0FBF3E` | Primary brand green |

Use these for: image scan (find pixels with this hex), or DOM filter by computed fill/color.

## Logo / image size (typical)

- **Small icon in button:** ~20–24px width, 20–24px height (square).
- **Render login button:** ~110px wide × 36px tall (whole button); icon is left-aligned inside.

Select by size: button with `width` 80–150px, `height` 30–50px, containing an `img` or `svg` with width/height ~16–28px.

## DOM selectors (clever)

1. **By image source/alt:**  
   `button:has(img[src*="github" i])`,  
   `button:has(img[alt*="GitHub" i])`,  
   `//button[.//img[contains(@src,'github') or contains(@alt,'GitHub')]]`

2. **By SVG fill (logo color):**  
   `//button[.//svg//*[contains(@fill,'000') or contains(@fill,'232925') or contains(@fill,'101411')]]`  
   (fill can be `#000`, `#232925`, `rgb(0,0,0)`, etc.)

3. **By logo size (img/svg ~24px):**  
   Button that contains an `img` or `svg` with naturalWidth/naturalHeight or getBoundingClientRect().width/height in 16–28px.

4. **By position (first social button):**  
   First `button` in the main form, or first of the four social buttons (GitHub, GitLab, Bitbucket, Google).

5. **By color scan (screenshot):**  
   Take screenshot → find regions where pixel hex is `#000000` or `#232925` → map to element via `elementFromPoint(x, y)`. Script: `find_by_color_scan.py`.

**Primary script:** `find_github_button_smart.py` tries (1) image src/alt, (2) XPath image, (3) size+logo, (4) SVG fill, (5) text. Use it for one-click GitHub login on Render.
