import { OpenDialogReturnValue } from "electron"
interface ElectronApi {
	promptToSelectDir: (filepath: string = "") => Promise<OpenDialogReturnValue>;
}
declare global {
	interface Window {
		electronApi: ElectronApi
	}
}
export { };
