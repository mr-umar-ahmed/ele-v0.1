const { contextBridge } = require('electron');

// This is a secure bridge between your React "Face" and Electron "Hands"
contextBridge.exposeInMainWorld('eleAPI', {
    // We will add commands here later!
});