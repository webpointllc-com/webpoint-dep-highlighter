# XPath reference for browser automation

Use XPath when snapshot refs are missing or to target elements reliably. Playwright: `page.locator("xpath=//...")`.

## Render login (dashboard.render.com/login)

| Element | XPath / selector |
|--------|--------|
| Log in with GitHub | `//button[contains(., 'GitHub')]` |
| **By logo image** | `//button[.//img[contains(@src,'github') or contains(@alt,'GitHub')]]` |
| **By logo color (hex)** | Scan screenshot for #000000 / #232925; elementFromPoint; or `//button[.//svg//*[contains(@fill,'000')]]` |
| **By size** | Button ~110×36px containing img/svg ~20–24px; first such button = GitHub |
| GitHub link (OAuth) | `//a[contains(@href, 'github')]` |
| GitLab | `//button[contains(., 'GitLab')]` |
| Google | `//button[contains(., 'Google')]` |
| Email input | `//input[@type='email']` or `//input[@placeholder='your@email.com']` |
| Password input | `//input[@type='password']` |
| Sign in (email) | `//button[contains(., 'Sign in')]` |

## GitHub (github.com/login)

| Element | XPath |
|--------|--------|
| Continue with Google | `//a[contains(@href, 'google')]` or `//button[contains(., 'Google')]` |
| Username/email input | `//input[@id='login_field']` |
| Password input | `//input[@id='password']` |
| Sign in | `//input[@name='commit']` |

## General

- Button by text: `//button[contains(normalize-space(), 'Text')]`
- Link by href: `//a[contains(@href, 'substring')]`
- By id: `//*[@id='id']`
- By data attribute: `//*[@data-testid='value']`
