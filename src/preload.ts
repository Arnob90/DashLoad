// See the Electron documentation for details on how to use preload scripts:
// https://www.electronjs.org/docs/latest/tutorial/process-model#preload-scripts
import { contextBridge, dialog, ipcMain, ipcRenderer, OpenDialogReturnValue } from "electron";
contextBridge.exposeInMainWorld("electronApi", {
	promptToSelectDir: (filepath: string = ""): Promise<OpenDialogReturnValue> => {
		const result = ipcRenderer.invoke("dialog:open", filepath) as Promise<OpenDialogReturnValue>
		return result;
	},
	saveMiscJson: async (obj: any): Promise<void> => {
		await ipcRenderer.invoke("saveMiscJson", obj)
	},
	getMiscJson: async (): Promise<any | null> => {
		return await ipcRenderer.invoke("getMiscJson")
	}
}
)

contextBridge.exposeInMainWorld('downloads', {
	download: (url: string, filepath: string) => ipcRenderer.invoke('download:download', url, filepath),
	pause: (id: string) => ipcRenderer.invoke('download:pause', id),
	resume: (id: string) => ipcRenderer.invoke('download:resume', id),
	getInfos: () => ipcRenderer.invoke('download:infos'),
	getInfo: (id: string) => ipcRenderer.invoke('download:info', id),
	pauseOrResume: (id: string) => ipcRenderer.invoke('download:pauseOrResume', id),
	cancel: (id: string) => ipcRenderer.invoke('download:cancel', id),
	delete: (id: string, deleteOnDisk: boolean) => ipcRenderer.invoke('download:delete', id, deleteOnDisk)
});
