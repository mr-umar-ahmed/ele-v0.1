const { app, BrowserWindow, ipcMain, shell } = require('electron');
const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');

function createWindow() {

  const win = new BrowserWindow({
    width: 1000,
    height: 700,

    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  win.loadURL('http://localhost:5173');
}

app.whenReady().then(() => {

  createWindow();

  app.on('activate', () => {

    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }

  });
});

app.on('window-all-closed', () => {

  if (process.platform !== 'darwin') {
    app.quit();
  }

});

// ==========================================
// ⚙️ THE EXECUTION ENGINE
// ==========================================

ipcMain.on('execute-task', (event, payload) => {

  console.log("FULL PAYLOAD:", payload);

  console.log(
    `[ELE EXECUTION] Intent Received: ${payload.intent}`
  );

  // ==========================================
  // ACTION 1: OPEN WEBSITE
  // ==========================================

  if (payload.intent === 'open_website') {

    console.log("Executing: Open Website...");

    const url = payload.target.startsWith('http')
      ? payload.target
      : `https://${payload.target}`;

    shell.openExternal(url).catch(err => {

      console.error(
        `Failed to open website: ${err}`
      );

    });
  }

  // ==========================================
  // ACTION 2: OPEN APP (DYNAMIC)
  // ==========================================

  else if (payload.intent === 'open_app') {

    console.log("Executing: Open App...");

    const appName = payload.target;

    const command =
      `powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-StartApps | Where-Object { $_.Name -match '${appName}' } | Select-Object -First 1 | ForEach-Object { Start-Process ('shell:AppsFolder\\' + $_.AppID) }"`;

    console.log("COMMAND:", command);

    exec(command, (error, stdout, stderr) => {

      if (error) {

        console.error(
          "Failed to open app:",
          error.message
        );

        return;
      }

      if (stderr) {

        console.error(
          "PowerShell stderr:",
          stderr
        );
      }

      console.log("stdout:", stdout);
    });
  }

  // ==========================================
  // ACTION 3: SEARCH WEB
  // ==========================================

  else if (payload.intent === 'search_web') {

    console.log("Executing: Search Web...");

    const query = encodeURIComponent(
      payload.target
    );

    shell.openExternal(
      `https://www.google.com/search?q=${query}`
    ).catch(err => {

      console.error(
        `Search failed: ${err}`
      );

    });
  }

  // ==========================================
  // ACTION 4: CREATE NOTE
  // ==========================================

  else if (payload.intent === 'create_note') {

    console.log("Executing: Create Note...");

    // Save notes in Documents/ELE_Notes

    const notesDir = path.join(
      app.getPath('documents'),
      'ELE_Notes'
    );

    // Create folder if not exists

    if (!fs.existsSync(notesDir)) {

      fs.mkdirSync(notesDir);

    }

    // Create filename

    const timestamp = new Date()
      .toISOString()
      .replace(/[:.]/g, '-');

    const filePath = path.join(
      notesDir,
      `note_${timestamp}.txt`
    );

    // Note content

    const noteContent =
`ELE NOTE RECORD
Created: ${new Date().toLocaleString()}
-------------------------
${payload.rawText}
`;

    // Save file

    fs.writeFile(
      filePath,
      noteContent,
      (err) => {

        if (err) {

          console.error(
            `Failed to write note: ${err.message}`
          );

        }

        else {

          console.log(
            `Note successfully saved to ${filePath}`
          );

        }

      }
    );
  }

  // ==========================================
  // UNKNOWN INTENT
  // ==========================================

  else {

    console.log(
      `Unknown intent received: ${payload.intent}`
    );

  }

});