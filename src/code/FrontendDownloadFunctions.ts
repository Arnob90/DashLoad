import { DownloadInfo, DefaultRequestOpts, downloadsListSchema, DownloadingInfo, DownloadsList } from "../code/DownloadFromServer";
export interface DownloadRequest {
	url: string
	filepath: string
}
export interface DownloadRequestResponse {
	id: string
}
export async function StartDownload(url: string, filepath: string) {
	const request: DownloadRequest = { filepath: filepath, url: url }
	await fetch("http://localhost:8000/download", {
		method: "POST",
		body: JSON.stringify(request),
		headers: DefaultRequestOpts.headers
	})
}
export async function CancelDownload(info: DownloadInfo) {
	fetch(`http://localhost:8000/download/cancel/${info.download_id}`, {
	})
}
export async function PauseDownload(info: DownloadInfo) {
	console.log(info)
	const id = info.download_id
	if (id === null) {
		throw new Error("The given id to pause is null")
	}
	if (info.type !== "DownloadingInfo") {
		throw new Error("Cannot pause a download that isn't even running")
	}
	const res = await fetch(`http://localhost:8000/download/pause/${id}`, {
		method: "POST",
		headers: DefaultRequestOpts.headers
	})
	if (!res.ok) {
		throw new Error("Cannot pause download")
	}
}
export async function ResumeDownload(info: DownloadInfo) {
	if (info.type !== "PausedDownloadInfo") {
		throw new Error("Cannot resume a download that isn't even paused")
	}
	const id = info.download_id
	if (id === null) {
		throw new Error("The id is missing")
	}
	try {
		await fetch(`http://localhost:8000/download/resume/${id}`, {
			headers: DefaultRequestOpts.headers,
			method: "POST"
		})
	}
	catch (err) {
		console.log(err)
	}
}
export async function ResumeOrPause(info: DownloadInfo) {
	if (info.type === "PausedDownloadInfo") {

		ResumeDownload(info)
	}
	else if (info.type === "DownloadingInfo") {
		console.log("Pausing download")
		PauseDownload(info)
	}
}
export async function RetryDownload(info: DownloadInfo) {
	if (info.type !== "FailedDownloadInfo") {
		throw new Error("Cannot retry a download that isn't even failed")
	}
	StartDownload(info.last_url, info.filepath)
}
interface DeleteRequest {
	delete_on_disk: boolean
}

export async function DeleteDownload(info: DownloadInfo, deleteLocalFile: boolean = false) {
	console.log(deleteLocalFile)
	const deleteRequest: DeleteRequest = { delete_on_disk: deleteLocalFile }
	try {
		await fetch(`http://localhost:8000/download/delete/${info.download_id}`, { method: "POST", headers: DefaultRequestOpts.headers, body: JSON.stringify(deleteRequest) })
	}
	catch (err) {
		console.log(err)
	}
}
