import { OpenDialogReturnValue } from "electron"
interface ElectronApi {
	promptToSelectDir: (filepath: string = "") => Promise<OpenDialogReturnValue>;
	saveMiscJson: (obj: any) => Promise<void>
	getMiscJson: () => Promise<any | null>;
}
declare global {
	interface Window {
		electronApi: ElectronApi
	}
}

declare global {
	interface Window {
		downloads: {
			download: (url: string, filepath: string) => Promise<DownloadRequestResponse>;
			pause: (id: string) => Promise<void>;
			resume: (id: string) => Promise<void>;
			getInfos: () => Promise<DownloadsList>;
			getInfo: (id: string) => Promise<DownloadInfo>;
			pauseOrResume: (id: string) => Promise<void>;
			cancel: (id: string) => Promise<void>;
			delete: (id: string, deleteOnDisk: boolean) => Promise<void>;
		};
	}
}
export { };
