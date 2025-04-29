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
export { };
