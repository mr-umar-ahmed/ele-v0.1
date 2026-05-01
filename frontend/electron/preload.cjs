const { contextBridge, ipcRenderer } = require('electron');

// This explicitly exposes a secure tunnel from React to Node.js
contextBridge.exposeInMainWorld('eleAPI', {
    executeTask: (payload) => ipcRenderer.send('execute-task', payload)
});