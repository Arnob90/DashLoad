export interface DownloadInfo {
	download_id: string | null
	filesize: number | null
	downloaded_file_portion: number | null
	filename: string | null
	filepath: string
}
export class DefaultRequestOpts {
	static headers = {
		'Accept': 'application/json',
		'Content-Type': 'application/json'
	}
}
export class DownloadInfoActions {
	static getDownloadProgress(givenInfo: DownloadInfo): number | null {
		if (givenInfo.downloaded_file_portion === null || givenInfo.filesize === null) {
			return null
		}
		return (givenInfo.downloaded_file_portion / givenInfo.filesize) * 100
	}
	static getSizeInMIB(givenSize: number) {
		return parseFloat((givenSize / (2 ** 20)).toFixed(1))
	}
}
