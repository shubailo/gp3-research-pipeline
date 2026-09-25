# GIT_DIAGNOSTIC_REPORT.md — Kizárólag Olvasó Git Rendszerdiagnosztika

> **Jelentés típusa:** Biztonsági és Rendszerarchitekturális Git Diagnosztika  
> **Vizsgálat jellege:** KIZÁRÓLAG OLVASÓ (Read-Only) — nulla fájlmódosítás, nulla git írási művelet  
> **Dátum:** 2026-09-25  
> **Fájl elérési út:** `c:\Users\shuba\Desktop\Researcher - Dóri\GIT_DIAGNOSTIC_REPORT.md`  

---

## 📌 VEZETŐI ÖSSZEFOGLALÓ (A LEGFONTOSABB BIZTONSÁGI TÉNYEK)

1. **NINCS ADATSZIVÁRGÁS (0 DB PUSH):**  
   Bár a távoli repó (`origin`) be van állítva a `https://github.com/shubailo/med-buddy.git` címre, **INNEN SOHA SEMMILYEN PUSH NEM TÖRTÉNT**.  
   A helyi repository-ban **EGYETLEN EGY COMMIT SEM LÉTEZIK (`No commits yet`)**, nincs reflog, és nincsenek távoli ágak (`git branch -r` üres). Külső szerverre erről a gépről semmi sem került fel.
2. **NINCS VERZIÓKÖVETVE ÉRZÉKENY FELHASZNÁLÓI ADAT (0 DB FÁJL):**  
   A `git ls-files` kimenete teljesen üres. Sem az `AppData`, sem a `Documents`, sem egyéb személyes profil-mappa **NINCS commitolva vagy indexelve (staging area üres)**. Minden fájl csupán követetlen (untracked) állapotban látható a munkakönyvtárban.
3. **GYÖKÉR-ELTÉRÉS OKA:**  
   A `.git` mappa fizikailag a `c:\Users\shuba` felhasználói könyvtárban található (létrehozva: 2025. 12. 30.), valószínűleg egy korábbi véletlen `git init` / `git remote add` következtében. A `c:\Users\shuba\Desktop\Researcher - Dóri` mappának **nincs saját `.git` könyvtára**, az a felhasználói profil repóján belül fekszik mint követetlen alkönyvtár.

---

## 1. A `.git` MAPPA PONTOS HELYE ÉS A REPÓ GYÖKERE

### Futtatott diagnosztikai parancs:
```powershell
git rev-parse --show-toplevel
Test-Path "c:\Users\shuba\Desktop\Researcher - Dóri\.git"
```

### Eredmény és Tények:
- **`git rev-parse --show-toplevel`:**  
  `C:/Users/shuba`
- **`Test-Path "c:\Users\shuba\Desktop\Researcher - Dóri\.git"`:**  
  `False`
- **`.git` mappa tényleges fizikai helye:**  
  `C:\Users\shuba\.git` (Rejtett mappa)
- **Létrehozás dátuma (`CreationTime`):**  
  `2025. 12. 30. 16:32:41`
- **Utolsó módosítás dátuma (`LastWriteTime`):**  
  `2026. 09. 25. 08:34:55`

**Megerősítés:** A git repository gyökere valóban a `C:\Users\shuba` felhasználói profil mappa, NEM pedig a `Researcher - Dóri` projektmappa.

---

## 2. TÁVOLI REPOSITORY BEÁLLÍTÁSA (`remote -v`)

### Futtatott diagnosztikai parancs:
```powershell
git remote -v
```

### Eredmény és Tények:
```
origin  https://github.com/shubailo/med-buddy.git (fetch)
origin  https://github.com/shubailo/med-buddy.git (push)
```

A `C:\Users\shuba\.git\config` fájl szó szerinti tartalma:
```ini
[core]
	repositoryformatversion = 0
	filemode = false
	bare = false
	logallrefupdates = true
	symlinks = false
	ignorecase = true
[lfs]
	repositoryformatversion = 0
[remote "origin"]
	url = https://github.com/shubailo/med-buddy.git
	fetch = +refs/heads/*:refs/remotes/origin/*
```

---

## 3. TÖRTÉNT-E MÁR PUSH A TÁVOLI SZERVERRE? (KRITIKUS BIZTONSÁGI VIZSGÁLAT)

### Futtatott diagnosztikai parancsok:
```powershell
git branch -r
git log --all --source --remotes
git show-ref
Test-Path "c:\Users\shuba\.git\logs"
```

### Eredmény és Tények:
- **`git branch -r` kimenete:**  
  *(Teljesen üres — nincsenek távoli ágak regisztrálva)*
- **`git log --all --source --remotes` kimenete:**  
  *(Teljesen üres — nincs egyetlen távoli commit sem a helyi git adatbázisban)*
- **`git show-ref` kimenete:**  
  *(Üres, Exit code: 1 — nincs egyetlen ref / tag / branch sem)*
- **`Test-Path "c:\Users\shuba\.git\logs"`:**  
  `False` *(Egyetlen git reflog bejegyzés sem jött létre soha a gépen)*

### 🔒 Biztonsági Megállapítás:
**NEM történt semmilyen push erről a gépről a GitHub szerverre.** Mivel a repóban nincs commit és nincs bejegyzés a távoli refekről, a felhasználói profilból semmilyen adat nem szivárgott ki a GitHubra.

---

## 4. MI VAN TÉNYLEGESEN VERZIÓKÖVETVE A PROFIL ÉRZÉKENY MAPPÁIBÓL?

### Futtatott diagnosztikai parancs:
```powershell
git ls-files | Select-String -Pattern "AppData|Documents|Music|Desktop\\(?!Researcher)"
git ls-files
git diff --cached --name-status
```

### Eredmény és Tények:
- **`git ls-files` kimenete:**  
  *(Teljesen üres — pontosan 0 darab fájl van indexelve/követve a repóban)*
- **PowerShell mintaillesztés kimenete:**  
  *(Nulla találat)*
- **`git diff --cached` (Staged fájlok):**  
  *(Teljesen üres — semmi sincs berakva az átmeneti tárba)*

### 🔒 Biztonsági Megállapítás:
A git kizárólag **követetlen fájlokként (untracked files)** látja a `C:\Users\shuba` alatti mappákat (`AppData`, `Documents`, `Music`, `Desktop`, stb.). Egyetlen privát állomány sincs bevonva a verziókövetésbe.

---

## 5. `.gitignore` FÁJLOK HELYZETE ÉS TARTALMA

A fájlrendszerben jelenleg **két darab** `.gitignore` fájl található:

### 5.1 A Profil Gyökérben: `C:\Users\shuba\.gitignore`
Teljes, szó szerinti tartalom:
```gitignore
# Local Netlify folder
.netlify
```

### 5.2 A Projekt Mappában: `C:\Users\shuba\Desktop\Researcher - Dóri\.gitignore`
Teljes, szó szerinti tartalom:
```gitignore
# Environment & secret files
.env
.env.local
*.key
*.pem
scratch/
```

---

## 6. COMMITOK SZÁMA, ELSŐ ÉS UTOLSÓ DÁTUMA

### Futtatott diagnosztikai parancs:
```powershell
git log --oneline | Measure-Object
git log --reverse --format="%ai" | Select-Object -First 1
git log --format="%ai" | Select-Object -First 1
git status
```

### Eredmény és Tények:
- **`git status` fejléc:**
  ```
  On branch main

  No commits yet
  ```
- **`git log` hibaüzenet:**
  ```
  fatal: your current branch 'main' does not have any commits yet
  ```
- **Commitok száma összesen:** **`0 db`**
- **Első commit dátuma:** *N/A (Nincs commit)*
- **Utolsó commit dátuma:** *N/A (Nincs commit)*

---

## 7. A `Researcher - Dóri` MAPPA STÁTUSZA

- **Saját `.git`:** A `c:\Users\shuba\Desktop\Researcher - Dóri` mappában **NINCS** `.git` könyvtár (`Test-Path` = False).
- **Beágyazott `.git` almappák:** A teljes projekt-hierarchiában (`meta_hyperglycaemia`, `src`, `data`, stb.) **egyetlen rejtett `.git` sem található**.
- **Kapcsolódás a szülő repóhoz:** A `Researcher - Dóri` mappa jelenleg csupán egy közönséges, **követetlen könyvtár (untracked directory)** a `C:\Users\shuba` mint munkakönyvtár alatt (a `git status`-ban mint `../` jelenik meg).

---

## 8. TISZTA TÉNYALAPÚ DIAGNÓZIS (ÖSSZEGZÉS A DÖNTÉSHEZ)

A tények alapján egyértelműen rekonstruálható a helyzet:
1. Valaki 2025. 12. 30-án a terminálban véletlenül a saját felhasználói profiljában (`C:\Users\shuba`) állva futtatta a `git init` és a `git remote add origin https://github.com/shubailo/med-buddy.git` parancsokat.
2. Ezt követően **sem `git add .`, sem `git commit`, sem `git push` nem történt**. A repó egy teljesen üres, "kezdeti" állapotban maradt.
3. Ezért semmilyen személyes adat, jelszó vagy fájl **nem került fel a GitHubra**, és helyileg sincs rögzítve a git történetben.
4. Ugyanakkor bármilyen git parancs (`git status`, stb.) jelenleg az egész Windows profil könyvtárat próbálja pásztázni, és ha valaki figyelmetlenül kiadna egy `git add .` parancsot a gyökérből, az a teljes felhasználói profilt megpróbálná indexelni.

*(A diagnosztika lezárult. Semmilyen írási vagy törlési parancs nem futott le. Várjuk a felhasználó döntését a következő lépésről.)*
