const { contextBridge, ipcRenderer } = require('electron');

// This exposes 'window.eleAPI' to React safely
contextBridge.exposeInMainWorld('eleAPI', {
    executeTask: (data) => ipcRenderer.send('execute-task', data)
});