import React, { use, useEffect, useState } from "react";
import { Button, buttonVariants } from "../components/ui/button";
import { Progress } from "@/components/ui/progress"
import "./styles/globals.css"
import "./styles/white-image.scss"
import { DownloadItem, DownloadList } from "./components/downloadlist";
import { ScrollArea } from "@/components/ui/scroll-area"
import { DownloadInfo, DefaultRequestOpts, DownloadInfoActions } from "./code/DownloadFromServer";
import { AddDownloadDialogButton } from "./components/AddDownloadDialog";
export interface DownloadRequest {
	url: string
	filepath: string
}
export interface DownloadRequestResponse {
	id: string
}
function useDownloadInfos() {
	const [downloadInfos, setDownloadInfos] = useState<DownloadInfo[]>([])
	const [continueExec, setContinueExec] = useState(true)
	async function updateDownloadInfos() {
		try {
			const request = await fetch("http://localhost:8000/download", {
				method: "GET",
				headers: DefaultRequestOpts.headers
			})
			const requestBody = await request.json()
			const requestItem = requestBody as DownloadInfo[]
			setDownloadInfos(requestItem)
		}
		catch (err) {
			console.error(err)
		}
		if (continueExec) {
			setTimeout(() => updateDownloadInfos(), 500)
		}
	}
	useEffect(() => {
		updateDownloadInfos()
		return () => {
			setContinueExec(false)
		}
	}, [])
	return downloadInfos;
}
export default function App() {
	const [downloadIds, setDownloadIds] = useState<string[]>([])
	const downloadInfos = useDownloadInfos()
	async function startDownload(url: string, filepath: string) {
		const request: DownloadRequest = { filepath: filepath, url: url }
		const res = await fetch("http://localhost:8000/download", {
			method: "POST",
			body: JSON.stringify(request),
			headers: DefaultRequestOpts.headers
		})
		const resBody = (await res.json()) as DownloadRequestResponse
		downloadIds.push(resBody.id)
		setDownloadIds(downloadIds);
	}
	return (
		<div className="grid grid-cols-1">
			<div className="flex flex-col">
				<div className="flex w-full py-2 border-2 border-b-gray-600 sticky">
					<AddDownloadDialogButton className="mx-3" submitEvent={(url: string, folderPath: string) => {
						startDownload(url, folderPath)
					}}>
						<div className="w-15 h-15 mx-2 bg-primary p-4">
							<img className="white-svg" src="../assets/plusicon.svg" />
						</div>
					</AddDownloadDialogButton>
					<Button className="w-15 h-15 bg-danger">
						<img className="white-svg" src="../assets/trash-bin-svgrepo-com.svg" />
					</Button>
				</div>
				<DownloadList>
					{downloadInfos.map((info: DownloadInfo) => {
						const progress = DownloadInfoActions.getDownloadProgress(info)
						return (
							<DownloadItem filename={info.filename} filesize={info.filesize} progress={progress} completedSize={DownloadInfoActions.getSizeInMIB(info.downloaded_file_portion)} />
						)
					})}
				</DownloadList>
			</div>
		</div>
	)
}
