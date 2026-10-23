# Fire HD 8 (7th gen, 2017) — Entrance Dashboard Setup

Goal: the Fire tablet lives at the entrance, plugged in, always showing the
entrance dashboard: **https://kdega77.github.io/home-dashboard/entrance.html**

The entrance page is a lite build made for this 2017 tablet (old browser):
big clock, current weather, rain chance, a "what to wear / umbrella" line,
sunrise–sunset, and a 4-day forecast. No TradingView (too heavy for this
tablet — that stays on the TV). It auto-dims between 11 PM and 6 AM and
reloads itself every 6 hours so it never gets stuck.

## Step 1 — Prep the tablet (5 min)

1. Connect to your home Wi-Fi.
2. Settings → Device Options → System Updates → let it update to the
   newest Fire OS it offers, then restart.
3. Settings → Device Options → Date & Time → confirm it's automatic
   (the dashboard clock uses the tablet clock).

## Step 2 — Keep the screen awake while plugged in

1. Settings → Device Options → tap **Serial Number** 7 times.
   A "Developer Options" entry appears.
2. Developer Options → turn ON **Stay awake** (screen will never sleep
   while charging).
3. Keep the tablet plugged in at the entrance — that's the deal: plugged
   in = screen on.

## Step 3 — Remove the lock screen friction

- Settings → Security & Privacy → if a lock-screen passcode/PIN is set,
  remove it (the dashboard tablet doesn't need one, and a PIN stops
  auto-recovery after a power blip).
- If your tablet shows ads on the lock screen ("Special Offers"), Fully
  Kiosk (next step) still works, but the tablet may wake to ads first.
  Options: ignore it, or remove ads via Amazon (one-time ~$20 in
  Settings → Special Offers, sometimes support removes it free if asked).

## Step 4 — Install Fully Kiosk Browser (the key app)

Fully Kiosk is the standard app for turning a Fire tablet into a
permanent dashboard. Free version is fine to start.

1. Open **Silk Browser** and go to **fully-kiosk.com** → Download the
   **Fully Kiosk Browser** APK (the Fire OS / Android version).
2. When asked, allow installs: Settings → Security & Privacy →
   **Apps from Unknown Sources** → allow Silk.
3. Open the downloaded APK and install Fully Kiosk Browser.
4. Open Fully Kiosk. Set these:
   - **Web Content Settings → Start URL:**
     `https://kdega77.github.io/home-dashboard/entrance.html`
   - **Device Management → Keep Screen On:** ON
   - **Device Management → Launch on Boot / Start on Boot:** ON
   - **Web Auto Reload → Auto Reload on Idle:** optional, the page
     already reloads itself every 6 hours.
   - **Kiosk Mode → Enable Kiosk Mode:** ON and set an exit PIN you'll
     remember (stops kids/guests from exiting the dashboard; exiting
     needs PIN + the Fully gesture).

## Step 5 — Optional but recommended: Fully Kiosk PLUS (~€8 one-time)

The PLUS licence unlocks the entrance-perfect feature:
**Motion Detection** — the front camera watches for movement, screen
turns ON when someone walks up to the door, OFF after ~1 minute idle.
Saves the screen and the battery vs. true 24/7-on.
Settings → Motion Detection → Enable Visual Motion Detection,
Screen On on Motion, Screen Off Timer ~60–120 s.
Buy the licence inside the app (per-device, one-time).

## Step 6 — Mount and power

- Stand it on an entrance console or use a tablet wall mount.
- Use the standard (slow) charger it came with, not a fast charger —
  gentler for a battery that stays plugged in for years.
- Route the cable so nobody trips / unplugs it.
- **Monthly check:** look at the tablet's back and edges. If the case
  bulges or the screen starts lifting, the 2017 battery is swelling —
  unplug it and retire the tablet. (Rare, but it's the one real risk of
  any always-plugged old tablet.)

## If something goes wrong

- Page looks frozen → Fully menu (swipe from left edge) → Reload.
- Tablet restarted → Fully auto-starts the dashboard (Step 4 setting).
- Wi-Fi dropped → the page keeps showing the clock and retries weather
  every 15 min; it recovers on its own when Wi-Fi returns.
- Want the TV version instead → change the Start URL back to
  `https://kdega77.github.io/home-dashboard/` (heavier; not recommended
  on this tablet).
