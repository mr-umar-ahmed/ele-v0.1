const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { exec } = require('child_process'); // This lets Node run terminal commands

function createWindow () {
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
});

// ==========================================
// ⚙️ THE EXECUTION ENGINE
// ==========================================
ipcMain.on('execute-task', (event, payload) => {
  console.log(`[ELE EXECUTION] Intent Received: ${payload.intent}`);

  if (payload.intent === 'open_app') {
    console.log("Opening browser...");
    
    // Cross-platform command to open the default browser
    let command;
    if (process.platform === 'win32') {
        command = 'start https://google.com'; // Windows
    } else if (process.platform === 'darwin') {
        command = 'open https://google.com'; // Mac
    } else {
        command = 'xdg-open https://google.com'; // Linux
    }

    exec(command, (error, stdout, stderr) => {
        if (error) {
            console.error(`Execution Error: ${error.message}`);
            return;
        }
    });
  }
  
  // TODO: Add 'create_note' logic next
});