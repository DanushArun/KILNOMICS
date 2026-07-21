# KILNOMICS

KILNOMICS is a local dashboard for analysing clinker-to-cement cost, quality,
energy, and model evidence from an Excel workbook. It runs on your computer;
the workbook is not uploaded to a cloud service.

This guide is written for someone using VS Code and Terminal for the first
time on a Mac.

## Before you start

You need these installed once:

- [VS Code](https://code.visualstudio.com/)
- Python 3.11 or later
- Node.js 20 or later

To check Python and Node, open **Terminal** and run these commands one at a
time:

```bash
python3 --version
node --version
```

Each command should print a version number. If either command says `command not found`, install that tool before continuing.

## Open the project in VS Code

1. Open VS Code.
2. Click **File** → **Open Folder…**.
3. Select the `pusu-pusu` folder.
4. Click **Open**.
5. In VS Code, click **Terminal** → **New Terminal**.

The panel at the bottom is the integrated terminal. It should show a path that
ends in `pusu-pusu`. If it does not, paste this command and press Enter:

```bash
cd /Users/danusharun/Downloads/pusu-pusu
```



## First-time setup

Run the following commands in the VS Code terminal, one at a time. Wait for a
command to finish before entering the next one.

```bash
python3 -m venv .venv
```

```bash
./.venv/bin/pip install -r requirements.txt
```

```bash
cd frontend
```

```bash
npm install
```

```bash
cd ..
```

You only need to do this setup once per project folder, unless you delete the
`.venv` or `frontend/node_modules` folders.

## Start KILNOMICS

KILNOMICS needs **two terminals** open at the same time.

### Terminal 1 — backend

1. In VS Code, click the `+` button in the Terminal panel to open a second
  terminal if you need one.
2. In the first terminal, make sure you are in the `pusu-pusu` folder.
3. Paste this command and press Enter:

```bash
./.venv/bin/uvicorn backend.app.main:app --reload --port 8000
```

Wait until you see this exact line:

```text
Uvicorn running on http://127.0.0.1:8000
```

Leave this terminal running. It is the part that reads Excel files and trains
the models.

### Terminal 2 — dashboard

1. Click the `+` button in the Terminal panel to open another terminal.
2. Paste these commands one at a time:

```bash
cd /Users/danusharun/Downloads/pusu-pusu/frontend
```

```bash
npm run dev
```

Wait until you see a line similar to this:

```text
Local: http://localhost:5173/
```

Hold `Command` and click the `http://localhost:5173/` link. Your browser opens
the dashboard.

## Run the demo workbook

1. In the dashboard, click **Demo workbook** to download the prepared example.
2. Click **Upload workbook**.
3. Select `KILNOMICS_Demo_Data.xlsx` from your Downloads folder.
4. The dashboard shows an in-progress training rail while it validates data,
  fits soft sensors, and builds the constrained value case. The rail reflects
  completed backend stages: queued, validation, model fitting, and analysis.
5. When analysis finishes, **Portfolio** shows the workbook-derived potential
  value pool, intensive operating position, and highest-value actions.
6. Open **Compare plants** to review intensive-only SHC gaps. Structural plant
  differences remain visible and are not presented as savings.
7. Open **Scenario** to test TSR above the current operating point. The result
  is bounded by the uploaded kiln capability and calculates ₹/t and annual
  potential from uploaded fuel prices, heat value, SHC, and production volume.
8. Open **Evidence & finance** to review model inputs, sample size, holdout
  performance, release decision, and finance-realised value.

The demo workbook is synthetic. Its results prove the software flow only; they
are not a claim about a real cement plant or realised savings.

## Use a real workbook

Use the same upload process for your `.xlsx` workbook. The backend validates
the required sheets, usable date coverage, and ranges before it trains models.

If a workbook is missing expected sheets or cannot be used for training, do not
make an operational decision from it. Fix the workbook first, then upload it
again.

## Stop the application

Click the terminal running the backend and press `Control` + `C` once. Then do
the same in the terminal running the dashboard. This stops the local servers;
it does not delete your Excel file or project files.

## Start it again

Open the project in VS Code and repeat only the two commands below in separate
terminals:

```bash
./.venv/bin/uvicorn backend.app.main:app --reload --port 8000
```

```bash
cd frontend && npm run dev
```



## Common issues



### `address already in use`

An older KILNOMICS server is still running. Find its terminal window and press
`Control` + `C`, then run the command again.

### `command not found: npm`

Node.js is not installed or VS Code needs to be restarted after installation.
Install the current long-term support version of Node.js, restart VS Code, and
run `node --version` to confirm it worked.

### The dashboard says the API is out of date

Stop the backend with `Control` + `C` and restart it using the backend command
above. Always include `--reload` while developing.

### Upload finishes but no model is eligible

This is an evidence result, not necessarily a software error. Open **Model
evidence & finance** to inspect model inputs, holdout performance, and failed
release gates.

### The upload rail does not appear

Restart both the backend and dashboard after pulling an update. The rail is
shown only while a workbook analysis is active; it disappears once the result
is ready.

## What the dashboard does not do yet

It does not autonomously control a kiln or present model correlations as causal
proof. Potential, validated, and finance-realised value are separate states. A
displayed saving becomes actionable only after a constrained scenario, plant
review, and finance validation.
