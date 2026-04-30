const { app, BrowserWindow } = require('electron');
const path = require('path');

function createWindow () {
  // This creates the actual desktop window
  const win = new BrowserWindow({
    width: 1000,
    height: 700,
    webPreferences: {
    preload: path.join(__dirname, 'preload.cjs'),
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  // This tells the window to load your React website!
  win.loadURL('http://localhost:5173');
}

app.whenReady().then(() => {
  createWindow();
});