# game.gigumbrajaguru.me

Sends `game.gigumbrajaguru.me` to the game page, `https://gigumbrajaguru.me/game/` (301,
query string kept). GitHub Pages serves only one custom domain per repo, so the
subdomain is answered by nginx on the `myseer` droplet (159.65.128.41).

1. **DNS:** add an `A` record `game` → `159.65.128.41` in the gigumbrajaguru.me zone.
2. **Install** from this repo's root on your machine:

   ```sh
   ssh myseer 'sudo bash -s' < deploy/game-subdomain/install.sh
   ```

   To use a Cloudflare origin certificate instead (needed for SSL mode "Full (strict)"):

   ```sh
   ssh myseer 'sudo CERT=/etc/ssl/gig/origin.crt KEY=/etc/ssl/gig/origin.key bash -s' < deploy/game-subdomain/install.sh
   ```

The script runs `nginx -t` before every reload and restores the previous config if it fails,
so the other sites on the droplet are never taken down. It is safe to re-run, e.g. after
DNS starts resolving, so that it can get a Let's Encrypt certificate.
