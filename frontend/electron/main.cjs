const { app, BrowserWindow, ipcMain, shell } = require('electron');
const path = require('path');
const fs = require('fs');

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
  console.log(`[ELE EXECUTION] Intent Received: ${payload.intent}`);

  // ACTION 1: OPEN APP (Upgraded to Native Shell)
  if (payload.intent === 'open_app') {
    console.log("Executing: Open Browser natively...");
    
    // shell.openExternal flawlessly handles OS-level default browser launching
    shell.openExternal('https://google.com').catch(err => {
        console.error(`Failed to open browser: ${err}`);
    });
  }
  
  // ACTION 2: CREATE NOTE
  else if (payload.intent === 'create_note') {
    console.log("Executing: Create Note...");
    
    // Create a 'notes' folder in the project root if it doesn't exist
    const notesDir = path.join(app.getAppPath(), '../../notes');
    if (!fs.existsSync(notesDir)){
        fs.mkdirSync(notesDir);
    }

    // Create a filename based on the timestamp
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filePath = path.join(notesDir, `note_${timestamp}.txt`);

    // Write the raw text from the user into the file
    const noteContent = `ELE NOTE RECORD\nCreated: ${new Date().toLocaleString()}\n---\n${payload.rawText}`;
    
    fs.writeFile(filePath, noteContent, (err) => {
        if (err) {
            console.error(`Failed to write note: ${err.message}`);
        } else {
            console.log(`Note successfully saved to ${filePath}`);
        }
    });
  }
});