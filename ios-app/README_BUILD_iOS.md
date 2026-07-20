# Build the 70.3 Tracker as a native iOS app (Capacitor)

This folder wraps your existing tracker (the same `index.html` that runs on the
web) into a real native iOS app you can run on a device and ship to TestFlight /
the App Store. Everything in `www/` is the app; Capacitor builds the native shell
around it.

You do this part on your **Mac**. It takes ~30–40 min the first time.

---

## 0. One-time prerequisites

1. **Install Xcode** — free from the Mac App Store (large download, be patient).
   After installing, open it once so it finishes setup, then run in Terminal:
   ```
   xcode-select --install
   sudo xcodebuild -license accept
   ```
2. **Install Node.js** (if you don't have it) — https://nodejs.org (LTS version).
3. **Install CocoaPods** (Capacitor uses it):
   ```
   sudo gem install cocoapods
   ```

## 1. Install dependencies & create the iOS project

In Terminal, `cd` into this `ios-app` folder, then:
```
npm install
npx cap add ios
npx cap sync ios
```
`cap add ios` creates an `ios/` folder containing a real Xcode project. You only
run `add` once; afterwards use `npx cap sync ios` to push web updates in.

## 2. Open in Xcode

```
npx cap open ios
```
In Xcode:
- Select the project in the left sidebar → **Signing & Capabilities** tab.
- Set **Team** to your Apple ID (add it under Xcode ▸ Settings ▸ Accounts if needed).
- Bundle identifier is already `com.manas.ironman703tracker` — change it if you like.

## 3. Run on your iPhone (free, no $99 needed for this part)

- Plug in your iPhone, select it as the run target at the top of Xcode, press ▶.
- The first time, on the phone go to **Settings ▸ General ▸ VPN & Device
  Management** and trust your developer certificate.
- A free Apple ID lets you run on your *own* device (the app expires after 7 days
  and must be re-run). To install on **friends' phones** you need TestFlight ⬇.

## 4. Share with friends via TestFlight (requires Apple Developer Program, $99/yr)

1. Enroll at https://developer.apple.com/programs (one-time $99/year).
2. In Xcode: **Product ▸ Archive**, then **Distribute App ▸ App Store Connect**.
3. In App Store Connect (appstoreconnect.apple.com), open **TestFlight**, add your
   friends as testers by email. They install the free **TestFlight** app and tap
   your invite. Builds last 90 days; no full App Store review needed for testers.

## 5. Publish to the App Store (optional, later)

From the same archive, choose App Store distribution, fill in the listing
(screenshots, description, privacy), and submit for review.

---

## Updating the app after you change the tracker

Whenever the web app changes, replace `www/index.html` (and assets) with the new
build, then:
```
npx cap sync ios
```
and re-run / re-archive in Xcode.

## ⚠️ Important: sign-in inside the installed app

The current sign-in uses an **email magic link**. When someone taps that link it
opens in Safari, which has a *separate* login session from the installed app — so
the installed app may not pick up the sign-in. The fix is to add a **6-digit code**
sign-in option (type the code straight into the app). Ask me to "add the OTP code
sign-in" and I'll wire it into both the web app and the Supabase email — it's a
small, additive change. Once signed in, the session persists, so this only matters
for that first login.
