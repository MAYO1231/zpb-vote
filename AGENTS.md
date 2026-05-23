# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## 專案概述

團契交接聚會即時投票網頁（盲眼劍客猜勝負）。**單一 `index.html` 檔案**，部署到 GitHub Pages。

- 參考實作：`D:\lawre\Downloads\職棒傳承.jsx`（React 版，邏輯與畫面可參考，但不用於此專案）
- 技術規格：`D:\lawre\Downloads\職棒傳承_技術規格.md`

---

## 技術架構

| 層 | 選擇 |
|----|------|
| 前端 | 純 HTML + Vanilla JS（無框架、無 build step） |
| 即時同步 | Firebase Realtime Database（`onValue()` WebSocket，不 polling） |
| 圓餅圖 | Chart.js 4（cdnjs，`<canvas>`，`chart.update()` 更新，不重建） |
| QR code | qrcodejs（cdnjs） |
| 字型 | Google Fonts：Noto Serif TC 900、Noto Sans TC |
| 部署 | GitHub Pages（靜態，單檔） |

---

## 檔案結構

```
/
└── index.html    ← 整個 app，全部邏輯與樣式都在這
```

---

## index.html 結構慣例

```
頂部設定區（使用者只需改這裡）
  └── <script> const FIREBASE_CONFIG = { ... } </script>

Firebase SDK（compat 版）
  └── firebase-app-compat.js + firebase-database-compat.js（gstatic CDN）

qrcodejs（cdnjs）
Chart.js（cdnjs）
Google Fonts

<style> ← 所有 CSS，含色彩 token、動畫

<body>
  主持人介面 / 參與者介面（依 URL param 切換，JS 控制顯示）

<script>
  FIREBASE_CONFIG 已在頂部宣告
  firebase.initializeApp(FIREBASE_CONFIG)
  const db = firebase.database()

  URL 路由（?mode=join → 參與者；否則 → 主持人）
  主持人邏輯
  參與者邏輯
```

---

## 即時同步

```javascript
// 讀：所有裝置共同監聽三條路徑
db.ref('/game').on('value', snap => { ... })
db.ref('/participants').on('value', snap => { ... })
db.ref('/predictions').on('value', snap => { ... })

// 寫：set() 或 update()
db.ref('/game').set(newGame)
db.ref('/game/phase').set('active')
```

---

## Firebase 資料結構

```
/game
  phase: "setup" | "active" | "finished"
  currentRoundIdx: number
  rounds/
    0/  id, label, p1, p2, status("pending"|"open"|"closed"), winner

/participants
  {name}/  name, joinedAt

/predictions
  {name}_{roundId}/  name, roundId, pick
```

---

## URL 路由

| URL | 畫面 |
|-----|------|
| `index.html` | 主持人 |
| `index.html?mode=join` | 參與者名字輸入 |
| `index.html?mode=join&name=小明` | 參與者投票/等待 |

名字輸入後用 `history.pushState()` 寫入 URL。

---

## 設計 Token（色彩）

```css
--bg: #080810;  --surface: #0f0f1c;  --card: #14141f;  --border: #1e1e2e;
--gold: #e8b84b;  --gold-dim: #a07a1a;
--red: #c94040;  --green: #2d7a4a;
--text: #e8e4dc;  --muted: #5a5870;  --dim: #2e2c3f;
```

動畫：`fadeIn`（畫面切換）、`pulse`（等待狀態文字）。

---

## Firebase Rules（使用者需手動貼入 Firebase Console）

```json
{ "rules": { ".read": true, ".write": true } }
```

---

## 狀態機

```
setup → [開始遊戲] → active
  round: pending → [開啟投票] → open → [標記勝者] → closed → currentRoundIdx++
  （最後一場 closed）→ finished
```

---

## 邊界情況

- Firebase 未設定 → 頁面頂部顯示紅色 banner
- `window.open()` 被擋 → `alert()` 提示
- 同名參與者 → 覆蓋（`/participants/{name}` 直接 set）
- 圓餅圖 → 無票時隱藏 canvas，顯示文字；有票才 `chart.update()`，不重建 instance
