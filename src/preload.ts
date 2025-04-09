// See the Electron documentation for details on how to use preload scripts:
// https://www.electronjs.org/docs/latest/tutorial/process-model#preload-scripts
import { contextBridge, dialog, ipcMain, ipcRenderer, OpenDialogReturnValue } from "electron";
contextBridge.exposeInMainWorld("electronApi", {
	promptToSelectDir: (filepath: string = ""): Promise<OpenDialogReturnValue> => {
		const result = ipcRenderer.invoke("dialog:open", filepath) as Promise<OpenDialogReturnValue>
		return result;
	}
}
)
