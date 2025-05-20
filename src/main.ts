import { app, BrowserWindow, ipcMain } from 'electron';
import path from 'node:path';
import fs from "fs/promises"
import started from 'electron-squirrel-startup';
import isDev from 'electron-is-dev';
import { dialog } from 'electron';
import { spawn } from 'node:child_process';
import { ChildProcess } from "node:child_process"
import treeKill from 'tree-kill';
if (started) {
	app.quit();
}
let backendProcess: ChildProcess | null = null;
const createWindow = () => {
	// Create the browser window.
	const mainWindow = new BrowserWindow({
		width: 800,
		height: 600,
		webPreferences: {
			preload: path.join(__dirname, 'preload.js'),
		},
	});

	// and load the index.html of the app.
	if (MAIN_WINDOW_VITE_DEV_SERVER_URL) {
		mainWindow.loadURL(MAIN_WINDOW_VITE_DEV_SERVER_URL);
	} else {
		mainWindow.loadFile(path.join(__dirname, `../renderer/${MAIN_WINDOW_VITE_NAME}/index.html`));
	}

	// Open the DevTools.
	mainWindow.webContents.openDevTools();
};

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.on('ready', () => {
	const backend_bin_path = path.join(process.resourcesPath, "server")
	if (!isDev) {
		backendProcess = spawn(backend_bin_path)
	}
	createWindow();
});

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
	if (process.platform !== 'darwin') {
		app.quit();
	}
});

app.on('activate', () => {
	// On OS X it's common to re-create a window in the app when the
	// dock icon is clicked and there are no other windows open.
	if (BrowserWindow.getAllWindows().length === 0) {
		createWindow();
	}
});

function cleanup_backend() {
	if (backendProcess !== null) {
		if (backendProcess.pid !== undefined) {
			treeKill(backendProcess.pid)
		}
		else {
			backendProcess.kill()
		}
	}
}

app.on("before-quit", cleanup_backend)

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and import them here.
ipcMain.handle("dialog:open", (event, defaultPath: string) => {
	const callingWindow = BrowserWindow.fromWebContents(event.sender);
	return dialog.showOpenDialog(callingWindow!, { defaultPath: defaultPath, properties: ["openDirectory"] })
});
ipcMain.handle("saveMiscJson", async (_, obj: any) => {
	const to_write_to = app.getPath("userData")
	console.log("Saving")
	console.log("Yooooo")
	console.log(obj)
	const obj_json = JSON.stringify(obj)
	try {
		await fs.writeFile(path.join(to_write_to, "misc.json"), obj_json)
	}
	catch (err) {
		console.log(err)
	}
})
ipcMain.handle("getMiscJson", async (_) => {
	const to_read_from = app.getPath("userData")
	let readJson;
	try {
		readJson = await fs.readFile(path.join(to_read_from, "misc.json"), "utf-8")
		console.log(readJson)
	}
	catch (err) {
		console.log(err)
		return null;
	}
	return JSON.parse(readJson);
})
