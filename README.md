# Trading Analyzer — APK Banane Ka Tarika

Ye folder ek complete Android app hai. APK khud build nahi karna padega —
GitHub free me cloud computer pe build karke de dega. Bas neeche steps follow karo.

## Files kya kar rahi hain
- `main.py` — App ka UI (Home screen, Stock/Forex input, Result screen)
- `core_logic.py` — Data fetch + BUY/SELL signal calculate karne ka logic
- `buildozer.spec` — APK build settings (app ka naam, permissions, etc.)
- `.github/workflows/build.yml` — Automatic build instructions GitHub ke liye

---

## STEP 1: GitHub account banao (agar nahi hai)
1. https://github.com pe jao
2. "Sign up" karo — free hai, sirf email chahiye

## STEP 2: Naya repository banao
1. Login karne ke baad, top-right corner me **+** icon pe click karo → **New repository**
2. Naam do: `trading-analyzer` (ya kuch bhi)
3. **Public** select karo (Private bhi chalega, but Public free build minutes zyada deta hai)
4. **Create repository** dabao
5. README/license add mat karo, khali rehne do

## STEP 3: Files upload karo
1. Apne nayi repository page pe, **"uploading an existing file"** link pe click karo
   (ya "Add file" → "Upload files")
2. Ye 4 files/folders is laptop/computer se drag-and-drop karo:
   - `main.py`
   - `core_logic.py`
   - `buildozer.spec`
   - `.github` (poora folder, jisme `workflows/build.yml` hai)
3. Niche **"Commit changes"** button dabao

   ⚠️ Important: `.github` folder ko bhi upload karna zaroori hai, warna automatic
   build start nahi hoga. Agar drag-drop me `.github` folder na jaye (kabhi browser
   hidden folders skip karta hai), to GitHub website pe "Add file" → "Create new file"
   se manually path likho: `.github/workflows/build.yml` aur uska content paste karo.

## STEP 4: Build automatically shuru ho jayega
1. Repository ke top pe **"Actions"** tab pe click karo
2. Tumhe ek workflow run dikhega chalta hua (yellow dot = running, green tick = done)
3. Pehli baar build hone me **15-25 minutes** lagte hain (Android SDK/NDK download
   hota hai) — patience rakho, browser band mat karo zaroorat nahi, ye cloud me chalta hai

## STEP 5: APK download karo
1. Jab build complete ho jaye (green tick ✅), us workflow run pe click karo
2. Sabse niche **"Artifacts"** section me `trading-analyzer-apk` dikhega
3. Usपe click karke zip download karo
4. Zip ke andar `.apk` file hai — usko apne phone pe transfer karo

## STEP 6: Phone pe install karo
1. APK file ko phone pe download/transfer karo (Google Drive, email, USB cable — kuch bhi)
2. Phone pe file open karo
3. Agar "Install blocked" ka warning aaye: **Settings → install karne do "unknown sources"
   se** (ye normal hai non-Play-Store apps ke liye, sirf is APK ke liye allow karo)
4. Install ho jayega, icon home screen pe aa jayega

---

## Agar build fail ho jaye (red ❌)
1. Actions tab me failed run pe click karo, error log padho
2. Sabse common issues:
   - `buildozer.spec` me koi typo — file dobara check karo
   - Kuch package version conflict — error message mujhe bhejo, main fix kar dunga
3. Fix karne ke baad, files ko phir se upload/commit karo — build phir se automatically chalega

## Future me changes karne ke liye
Jab bhi `main.py` ya `core_logic.py` me koi change karke GitHub pe upload/commit karoge,
naya build automatically shuru ho jayega — koi extra step nahi.
