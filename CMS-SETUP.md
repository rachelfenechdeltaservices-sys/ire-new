# Top 10 Irish Casino – CMS (Sveltia CMS)

Edit every piece of text on the website, reorder the sportsbook and casino offers, and add or remove
operator reviews from a browser at **https://top10irishcasino.site/admin/** – signing in with a
**username and password**.

```
 You (browser)                Your web host (PHP)                    GitHub
 ─────────────                ───────────────────                    ──────
 /admin/  ── Sign in ──►  admin/auth.php  checks username/password
                          reads  cms-private/cms-config.php  ──────► token for the repository
 Edit & Save ─────────────────────────────────────────────────────► content/*.json committed
                                                                     │
                          public_html/  ◄── FTP upload ◄── GitHub Action rebuilds the HTML pages
```

---

## What's where

| Path | What it is |
|---|---|
| `updated-website/content/` | **All website text** as JSON files (offers, pages, reviews, FAQ, settings). This is what the CMS edits. |
| `updated-website/_cms/build.py` | Turns the content into the HTML pages (`index.html`, `casino.html`, reviews …). |
| `updated-website/_cms/cms-config.source.yml` | CMS fields definition (generates `admin/config.yml`). |
| `updated-website/admin/` | The CMS: `index.html` (Sveltia CMS 0.268.0, self-hosted), `auth.php` (username/password sign-in), `backend.php`, `make-password.php`. |
| `cms-private/cms-config.example.php` | **Template for the special private file** with the GitHub account details and the CMS logins. |
| `.github/workflows/cms-build-deploy.yml` | Rebuilds the pages after every content change and uploads the site by FTP. |

---

## One-time setup

### 1. Create a GitHub access token (the account the site's content is stored on)

Signed in to GitHub **as the account that owns or can write to `rachelfenechdeltaservices-sys/ire-new`**:

1. GitHub → your profile picture → **Settings** → **Developer settings** → **Personal access tokens** → **Fine-grained tokens** → **Generate new token**.
2. **Token name:** `Top 10 Irish Casino CMS`. **Expiration:** up to 1 year (put a reminder in your calendar).
3. **Repository access:** *Only select repositories* → `ire-new`.
4. **Permissions → Repository permissions → Contents:** **Read and write** (Metadata read-only is added automatically).
5. **Generate token** and copy it (it starts with `github_pat_`). You'll only see it once.

### 2. Create the private settings file on your server

1. Copy `cms-private/cms-config.example.php` and name the copy **`cms-config.php`**.
2. In it, fill in:
   - `'repo'` – `rachelfenechdeltaservices-sys/ire-new` (already filled in)
   - `'branch'` – the branch the live site is published from (`adding-cms` for now)
   - `'token'` – the token from step 1
3. Upload it with cPanel **File Manager** (or FTP) to a folder named **`cms-private` next to – not inside – `public_html`**:

   ```
   /home/<your-cpanel-user>/cms-private/cms-config.php   ← the private file
   /home/<your-cpanel-user>/public_html/                  ← the website
   ```

   It can also go directly in `public_html/cms-config.php` (or `public_html/admin/cms-config.php`):
   the `.htaccess` files block it from being opened or downloaded, and the login-attempt log is then
   kept in the server's temporary folder instead of the public folder.

> **Never commit `cms-config.php` to GitHub or email it.** `.gitignore` already keeps it out of the repository.

### 3. Create your CMS username and password

1. Open **https://top10irishcasino.site/admin/make-password.php**.
2. Enter a username and a password (12+ characters) → **Create login line**.
3. Copy the line it shows, e.g. `'rachel' => '$2y$10$…',`, into the `'users' => [ … ]` list in
   `cms-config.php` and save. Repeat for each person who needs access.

Passwords are stored only as one-way hashes. After 5 wrong passwords from the same IP address, sign-in is
blocked for 15 minutes (change `max_attempts` / `lockout_minutes` in `cms-config.php`).

### 4. Automatic publishing after each save (GitHub Action)

In GitHub → repository **Settings** → **Secrets and variables** → **Actions**:

| Type | Name | Value |
|---|---|---|
| Secret | `FTP_SERVER` | FTP host from your hosting panel, e.g. `ftp.top10irishcasino.site` |
| Secret | `FTP_USERNAME` | FTP username |
| Secret | `FTP_PASSWORD` | FTP password |
| Variable (optional) | `FTP_SERVER_DIR` | Folder on the server, default `public_html/` |
| Variable (optional) | `FTP_PROTOCOL` | `ftps` (default) or `ftp` if your host doesn't support FTPS |
| Variable (optional) | `DEPLOY_BRANCH` | Branch to publish, default `adding-cms` |

Also check **Settings → Actions → General → Workflow permissions** allows *Read and write permissions*.

Each time content is saved in the CMS (or anyone pushes a change under `updated-website/`), the
**Build & deploy website** action: rebuilds the HTML pages → commits them → uploads the site to
`public_html/` (skipping `content/`, `_cms/` and the private file). A save is usually live within
1–2 minutes. Without the FTP secrets the action still rebuilds and commits the pages; you can then
upload `updated-website/` yourself.

**First upload:** run the action once by hand (GitHub → **Actions** → *Build & deploy website* → **Run workflow**),
or upload the contents of `updated-website/` to `public_html/` with your hosting File Manager.

---

## Using the CMS

Go to **https://top10irishcasino.site/admin/** → **Sign In with Username & Password** → enter your login in
the window that opens.

- **Offers → Sportsbook offers / Casino offers**
  - **Change the ranking:** drag an offer by its handle, or use **Move Up / Move Down** in the item's menu.
    The first offer is #1 and gets the *Top Pick* ribbon; numbers update automatically.
  - **Hide an offer** without deleting it: switch off *Show on the website*.
  - **Add an offer:** *Add offer* at the bottom of the list. Upload the logo there.
  - *Review page* links an offer to a review: it adds the "Read … review" link, and the review page shows that
    offer's welcome bonus and visit buttons.
  - *Operator terms* – paste the operator's significant terms exactly as supplied.
  - *Short link* – the address the Visit buttons use, e.g. `/link1` (see **Offer short links** below).
- **Reviews** – edit, add (**New Review**) or delete operator reviews. Each review gets its own page and is
  added to the *Reviews* menu and the footer automatically. *Position in menu* sets the menu order.
- **Pages** – the text of the homepage, casino page, About, FAQ page, Contact, guide, responsible
  gambling and all legal pages.
- **FAQ** – the questions on the FAQ page (drag to reorder; the first ones also show on the homepage).
- **Site settings** – site name, domain, contact email, helpline, "updated" month, header/footer text,
  offer button labels and the responsible-gambling banner.

**Shortcuts you can type in any text:** `{{site_name}}`, `{{email}}`, `{{domain}}`, `{{helpline}}` are replaced
with the values from *Site settings*, so changing the email there updates it everywhere.
Text boxes accept **bold** (`**bold**`) and links (`[link text](page.html)`).

Click **Save** to publish. Sign out from the account menu when you're on a shared computer.

---

## Offer short links (`/link1`, `/link2` …) and `.htaccess`

Every Visit / Claim button links to a short address on your own site, which `updated-website/.htaccess`
redirects to the affiliate URL. Each offer keeps its own short link when you reorder offers.

| Short link | Offer | Short link | Offer |
|---|---|---|---|
| `/link1` | 3et (sportsbook) | `/link8` | QuinnCasino (casino) |
| `/link2` | QuinnBet (sportsbook) | `/link9` | Novibet (casino) |
| `/link3` | Novibet (sportsbook) | `/link10` | NetBet (casino) |
| `/link4` | NetBet (sportsbook) | `/link11` | LiveScore Vegas (casino) |
| `/link5` | LiveScore Bet (sportsbook) | `/link12` | TonyBet (casino) |
| `/link6` | Midnite (sportsbook) | `/link13` | Midnite (casino) |
| `/link7` | TonyBet (sportsbook) | | |

Review pages use the same short link as the linked offer.

You can set up the redirects in either of two ways:

1. **From the CMS (recommended):** fill in the offer's **Affiliate destination**. On the next rebuild the
   redirect is written into `.htaccess` automatically, inside the block marked
   `# BEGIN CMS offer links` … `# END CMS offer links`.
   - Put `{gclid}` where the Google Ads click ID belongs, e.g. `https://partner.example/?c={gclid}`.
   - Without `{gclid}`, the visitor's query string (including `?gclid=…`) is passed on to the destination.
2. **By hand:** leave *Affiliate destination* empty and add your own rule to `updated-website/.htaccess`
   **outside** the generated block, for example:

   ```apache
   RewriteRule ^link1/?$ https://partner.example/track?c=123 [R=302,L,NE,QSA]
   ```

   Rules outside the block are never changed by the build.

Redirects are temporary (302), so browsers don't cache an old destination when an affiliate link changes.
For a new offer, pick the next free number (`/link14`, …). If two offers share a short link but point to
different destinations, the build keeps only the first and prints a warning.

---

## For developers

```bash
pip install "markdown>=3.5,<4" "PyYAML>=6,<7"
python updated-website/_cms/build.py        # rebuild pages + admin/config.yml from content
```

- Add/change CMS fields in `updated-website/_cms/cms-config.source.yml` (shared definitions live under `x-` keys),
  then run the build to regenerate `admin/config.yml`.
- Page markup is in `updated-website/_cms/templates.py` and `build.py`.
- Sveltia CMS is self-hosted in `admin/sveltia/` (version in `VERSION.txt`). To upgrade, replace
  `sveltia-cms.js` and `chunks/` with the `dist/` files of a newer `@sveltia/cms` npm package.

### How the username/password sign-in works

Sveltia CMS talks to GitHub directly from the browser with a GitHub token. Instead of GitHub's own login,
`admin/backend.php` points Sveltia's sign-in button at `admin/auth.php`. That page asks for a username and
password (checked against the hashes in `cms-config.php`, with brute-force lockout and CSRF protection) and only
then hands the token from `cms-config.php` back to the CMS window using Sveltia's standard popup handshake. The
token is never in the public website files or the repository.

After sign-in, Sveltia keeps the token in the browser's local storage until you sign out – so use **Sign Out**
on shared computers. If a token is ever exposed, revoke it on GitHub and put a new one in `cms-config.php`.

### Troubleshooting

| Problem | Fix |
|---|---|
| *"CMS not set up"* / config error when opening `/admin/` | `cms-config.php` isn't found – check its name and folder (step 2). |
| Sign-in window says *"No CMS users are set up"* | Add a line to `'users'` (step 3). |
| Signed in, then *"Bad credentials"* or *permission* error | Token expired, mistyped, or lacks **Contents: Read and write** on `ire-new`. |
| *Too many failed attempts* | Wait for the lockout (default 15 min) or delete `.cms-login-attempts.json` next to `cms-config.php`. |
| Changes saved but not on the website | Check GitHub → **Actions** for the latest *Build & deploy website* run and its FTP step. |
