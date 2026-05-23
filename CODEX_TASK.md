# Codex Task Spec — 職棒傳承

> Planner 文件，供 Codex 實作用。請完整閱讀後再開始。

---

## Goal

將 `D:\lawre\Downloads\職棒傳承.jsx`（React + 自訂 storage）移植為單一 `index.html`，改用 Firebase Realtime Database 做即時同步，可直接部署到 GitHub Pages，無需任何 build 工具。

---

## Scope

**可修改：**
- `index.html`（本專案唯一目標檔案，從零建立）

**僅供參考，不可修改：**
- `D:\lawre\Downloads\職棒傳承.jsx` — UI 畫面與邏輯的參考實作
- `D:\lawre\Downloads\職棒傳承_技術規格.md` — 完整規格文件
- `CLAUDE.md` — 架構說明

**不可建立：**
- 任何 JS 模組、CSS 檔、build config、`package.json`

---

## Required changes

### 1. HTML 骨架與設定區

在 `index.html` 最頂部建立明確的使用者設定區：

```html
<!-- ★ 使用者設定區 — 只需修改這裡 ★ -->
<script>
  const FIREBASE_CONFIG = {
    apiKey: "YOUR_API_KEY",
    authDomain: "YOUR_PROJECT.firebaseapp.com",
    databaseURL: "https://YOUR_PROJECT-default-rtdb.firebaseio.com",
    projectId: "YOUR_PROJECT_ID",
    storageBucket: "YOUR_PROJECT.appspot.com",
    messagingSenderId: "YOUR_SENDER_ID",
    appId: "YOUR_APP_ID"
  };
</script>
```

接著依序載入：
1. Firebase compat SDK（gstatic CDN，版本 10.7.1）：`firebase-app-compat.js`、`firebase-database-compat.js`
2. qrcodejs（cdnjs 1.0.0）
3. Chart.js（cdnjs 4.4.1）
4. Google Fonts：Noto Serif TC（700, 900）、Noto Sans TC（400, 500, 700）

**驗收：** 頁面開啟時若 `FIREBASE_CONFIG.databaseURL` 仍為預設值，頁面頂部顯示紅色 banner「⚠️ 請先填入 Firebase 設定」，並停止初始化。

---

### 2. CSS — 設計 Token 與動畫

在 `<style>` 中定義 CSS 變數與全域樣式：

```css
:root {
  --bg: #080810; --surface: #0f0f1c; --card: #14141f; --border: #1e1e2e;
  --gold: #e8b84b; --gold-dim: #a07a1a;
  --red: #c94040; --green: #2d7a4a;
  --text: #e8e4dc; --muted: #5a5870; --dim: #2e2c3f;
}
@keyframes fadeIn { from { opacity:0; transform:translateY(8px); } to { opacity:1; transform:translateY(0); } }
@keyframes pulse  { 0%,100% { opacity:1; } 50% { opacity:0.5; } }
.fade-in { animation: fadeIn 0.3s ease forwards; }
.pulse   { animation: pulse 2s ease-in-out infinite; }
```

字型全站：`font-family: 'Noto Sans TC', sans-serif`。標題（App 名稱、場次名）：`'Noto Serif TC', serif, font-weight: 900`。

**驗收：** 暗色背景，文字可讀，標題字型正確套用。

---

### 3. URL 路由

```javascript
function getMode() { return new URLSearchParams(location.search).get('mode'); }
function getNameParam() {
  const n = new URLSearchParams(location.search).get('name');
  return n ? decodeURIComponent(n) : '';
}
function pushNameToURL(name) {
  const url = new URL(location.href);
  url.searchParams.set('mode', 'join');
  url.searchParams.set('name', encodeURIComponent(name));
  history.pushState({}, '', url.toString());
}
```

- `?mode=join` → 渲染參與者介面
- 其他 → 渲染主持人介面

**驗收：** 同一網址加上 `?mode=join` 顯示完全不同的介面。

---

### 4. Firebase 初始化與即時同步

```javascript
firebase.initializeApp(FIREBASE_CONFIG);
const db = firebase.database();

// 三條監聽路徑（主持人與參與者都需要）
db.ref('/game').on('value', snap => { /* 更新 UI */ });
db.ref('/participants').on('value', snap => { /* 更新名單 */ });
db.ref('/predictions').on('value', snap => { /* 更新投票 */ });
```

**⚠️ 風險：** 禁止用 polling（`setInterval`）做同步，一律用 `onValue()` listener。

**驗收：** 兩個瀏覽器分頁開啟同一頁面，主持人操作後參與者畫面在 1 秒內自動更新。

---

### 5. Firebase 資料結構

嚴格遵守以下結構，不得增減欄位：

```
/game
  phase: "setup" | "active" | "finished"
  currentRoundIdx: number
  rounds/
    0/ { id, label, p1, p2, status: "pending"|"open"|"closed", winner: null|string }
    1/ ...

/participants
  {name}/ { name: string, joinedAt: number }

/predictions
  {name}_{roundId}/ { name: string, roundId: string, pick: string }
```

---

### 6. 主持人介面（4 個 Tab）

Tab 切換用 JS 控制 `display: none / block`，不做頁面跳轉。

#### Tab 1 — 設定

- QR code 元件（qrcodejs，200×200，白色圓角容器），指向 `當前URL?mode=join`
- 「↗ 在新視窗顯示 QR Code」按鈕：`window.open()` 開啟新視窗，`document.write()` 寫入完整白底 HTML，QR 280×280。若 `window.open()` 回傳 null，`alert('請在瀏覽器允許此頁面開啟彈出視窗後再試')`
- 新增場次表單：場次名稱（選填）、選手A、選手B；送出後寫入 `/game/rounds`
- 已新增場次列表，`phase === "setup"` 時每場可刪除
- 「▶ 開始遊戲」按鈕（需至少 1 場）：將 `/game/phase` 設為 `"active"`，`currentRoundIdx` 設為 `0`
- `phase !== "setup"` 時顯示「遊戲進行中 — 切換到遊戲分頁操作」

#### Tab 2 — 遊戲控制

依 `phase` 顯示不同內容：

- `setup`：「請先在設定頁開始遊戲」
- `finished`：「🏁 遊戲已結束，查看排名頁」
- `active`：
  - 目前場次卡片（label、p1 vs p2、status badge）
  - `status === "pending"`：「🗳 開啟投票」按鈕 → 將該 round 的 status 設為 `"open"`
  - `status === "open"`：
    - 「X / Y 人已投票」（Y = participants 總數）
    - 圓餅圖（Chart.js donut）：p1 金色、p2 紅色；無票時隱藏 canvas 顯示文字「等待第一票...」；有票時 `chart.update()`，不重建 instance
    - 「🏆 [p1]」和「🏆 [p2]」標記勝者按鈕
  - 標記勝者後：status → `"closed"`，winner 寫入，`currentRoundIdx + 1`；若為最後一場則 `phase → "finished"`，自動切換到排名 Tab
  - 已完成場次列表（label、對戰、勝者）

#### Tab 3 — 名單

- 列出所有 `/participants` 成員
- 若目前 `status === "open"`，每人後顯示「✓ 已投票」或「○ 待投票」

#### Tab 4 — 排名

- 任何時候可查看（即時計算猜對場數）
- 排名：名次（🥇🥈🥉 / 數字）、名字、猜對場數
- `phase === "finished"` 時第 1 名卡片加金色邊框
- 「重置」按鈕（Header 右上角，非 Tab 內）：清空 `/game`、`/participants`、`/predictions`，回到 setup

---

### 7. 參與者介面（依狀態自動切換）

所有切換靠 `onValue()` listener 驅動，不需手動操作。

| 條件 | 畫面 |
|------|------|
| URL 無 `name` param | 名字輸入頁（autofocus，Enter 送出，按鈕加入） |
| `phase === "setup"` | 「等待主持人開始遊戲...」+ pulse 動畫 |
| `phase === "active"` 且 `round.status === "pending"` | 顯示場次名稱、p1 vs p2、「等待主持人開啟投票...」 |
| `round.status === "open"` 且未投票 | 兩個全寬大按鈕（p1 / p2），垂直排列 |
| `round.status === "open"` 且已投票 | 「已投給：[pick]」+ 「等待結果...」pulse |
| `round.status === "closed"` | 本場勝者 + 猜對（🎯）/ 猜錯（😅）/ 未投票（📋）+ 「等待下一場...」pulse |
| `phase === "finished"` | 個人成績（猜對 X/Y 場，第 Z 名）+ 完整排名表，自己那行金色邊框標示 |

**加入流程：**
1. 寫入 `/participants/{name}`
2. `pushNameToURL(name)`
3. 畫面切換到等待/投票畫面

**投票流程：**
1. 寫入 `/predictions/{name}_{roundId}`
2. 本地立即切換到「已投票，等待結果」畫面

---

### 8. QR Code 元件（主持人設定頁內嵌）

```javascript
// 僅初始化一次，URL 改變時重建
function renderQR(url, size) {
  const container = document.getElementById('qr-box');
  container.innerHTML = '';
  new QRCode(container, { text: url, width: size, height: size, colorDark: '#111', colorLight: '#fff' });
}
```

---

## Acceptance criteria

1. **單檔可用**：直接用瀏覽器開啟 `index.html`（填入真實 Firebase config 後），主持人與參與者流程可完整跑完，無 console error
2. **即時同步**：兩個分頁，主持人操作後 1 秒內參與者畫面更新，無需重新整理
3. **QR code**：設定頁內嵌 QR 正確顯示；新視窗按鈕可開啟白底大 QR
4. **圓餅圖**：無票時不顯示 canvas；第一票投入後出現圖表；後續票數更新圖表（不閃爍重建）
5. **狀態機正確**：setup → active → (pending → open → closed)×N → finished，所有裝置同步
6. **排名正確**：每位參與者猜對場數計算準確，支援多人同分並列
7. **重置**：重置後所有裝置回到 setup 畫面，Firebase 資料清空
8. **Firebase 未設定**：顯示紅色 banner，不拋出 uncaught error

---

## Forbidden changes

- 禁止引入任何框架（React、Vue、Svelte 等）
- 禁止使用 `setInterval` 做資料同步（圖表更新除外）
- 禁止建立 `index.html` 以外的任何檔案
- 禁止使用 Firebase modular SDK（只用 compat 版，`firebase.database()`）
- 禁止在圓餅圖有新資料時銷毀並重建 Chart instance（使用 `chart.data.datasets[0].data = [...]; chart.update()`）
- 禁止修改 `CLAUDE.md`、`CODEX_TASK.md`

---

## Questions

無。規格文件與參考實作已足夠完整，可直接實作。
