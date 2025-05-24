import React, { useRef, useEffect, useState } from "react";
import { Button } from "../components/ui/button";
import "./styles/globals.css"
import "./styles/white-image.scss"
import { DownloadTable } from "./components/downloadlist";
import { DownloadInfo, DefaultRequestOpts, downloadsListSchema, DownloadingInfo, DownloadsList } from "./code/DownloadFromServer";
import { AddDownloadDialogButton } from "./components/AddDownloadDialog";
import { DownloadDeleteDialog } from "./components/DownloadDeleteDialog"
import { GetDownloads, StartDownload, CancelDownload, PauseDownload, ResumeOrPause, ResumeDownload, RetryDownload, DeleteDownload } from "./code/FrontendDownloadFunctions";
import addSvg from "../assets/plusicon.svg"
import deleteSvg from "../assets/trash-bin-svgrepo-com.svg"
function useDownloadInfos(): DownloadInfo[] {
	const [downloadInfos, setDownloadInfos] = useState<DownloadsList>([])
	const [continueExec, setContinueExec] = useState(true)
	let requestBody: any;
	async function updateDownloadInfos() {
		try {
			const requestItem = await GetDownloads()
			setDownloadInfos(requestItem)
		}
		catch (err) {
			console.error(err)
			console.log(requestBody)
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
function useMockDownloadInfos() {
	const requiredMocks: DownloadInfo[] = [{ download_id: "afjojfoajfoi", filepath: "/home/arnob/DownloadsTest/1.3GBiconpng", downloaded_file_portion: 39040499, filesize: 3901938090, filename: "Sus", type: "DownloadingInfo", download_speed: 1 } as DownloadingInfo]
	return requiredMocks
}

export default function App() {
	const downloadInfos = useDownloadInfos()
	const [dialogOpen, setDialogOpen] = useState(false)
	const [focusedDownloadInfo, setFocusedDownloadInfo] = useState<DownloadInfo | null>(null)
	async function startDownloadHelper(url: string, filepath: string) {
		setDialogOpen(false)
		await StartDownload(url, filepath)
	}
	async function DeleteDownloadInfo(deleteLocalFile: boolean = false) {
		if (focusedDownloadInfo !== null) {
			await DeleteDownload(focusedDownloadInfo, deleteLocalFile)
		}
	}
	return (

		<div className="grid grid-cols-1">

			<AddDownloadDialogButton submitEvent={(url: string, folderPath: string) => {
				startDownloadHelper(url, folderPath)
			}} dialogOpen={dialogOpen} dialogOpenStatusChangeRequest={setDialogOpen} />
			<div className="flex flex-col">
				<div className="flex w-full py-2 border-2 border-b-gray-600 sticky">
					<Button className="w-15 h-15 mx-2 bg-primary p-4" onClick={() => { setDialogOpen(true) }}>
						<img className="white-svg" src={addSvg} />
					</Button>
					<DownloadDeleteDialog deleteConfirmationCallback={DeleteDownloadInfo}>
						<Button className="w-15 h-15 bg-destructive" onMouseDown={(e) => { e.preventDefault() }}>
							<img className="white-svg" src={deleteSvg} />
						</Button>
					</DownloadDeleteDialog>
				</div>
				<DownloadTable downloadInfos={downloadInfos} pausedOrPlayButtonPressedEventHandler={ResumeOrPause} retryButtonPressedEventHandler={RetryDownload} focusChangedEventHandler={(info) => { setFocusedDownloadInfo(info) }}></DownloadTable>
			</div>
		</div>

	)
}
