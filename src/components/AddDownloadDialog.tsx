import React, { Children, useEffect, useRef, useState } from "react";
import { ReactNode } from "react";
import { DialogHeader, DialogTrigger, DialogTitle, DialogDescription, DialogContent, Dialog, DialogFooter } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { SerializedMisc, GetSerializedMisc, SaveSerializedMisc } from "../code/MiscObj"
interface AddDownloadDialogButtonProps {
	submitEvent?: (url: string, folderPath: string) => void;
	dialogOpen: boolean;
	dialogOpenStatusChangeRequest?: (statusRequested: boolean) => void;
}
export function AddDownloadDialogButton({ submitEvent, dialogOpen, dialogOpenStatusChangeRequest }: AddDownloadDialogButtonProps) {
	const [chosenUrl, setChosenUrl] = useState<string | null>(null);
	const [choosenFolder, setChoosenFolder] = useState<string | null>(null)
	const [misc, setMisc] = useState<SerializedMisc>({ lastUsedUrl: "", lastUsedDownloadFolder: "" })
	useEffect(() => {
		(async () => {
			const gottenMisc = await GetSerializedMisc()
			setMisc(gottenMisc)
			setChosenUrl(gottenMisc.lastUsedUrl)
			setChoosenFolder(gottenMisc.lastUsedDownloadFolder)
		})()
	}, [])
	async function selectFolder() {
		const choosen_filepath = await window.electronApi.promptToSelectDir()
		const choosen_filepaths_arr = choosen_filepath.filePaths
		if (choosen_filepaths_arr.length !== 1) {
			return;
		}
		setChoosenFolder(choosen_filepaths_arr[0])
	}
	async function SaveMisc() {
		const miscToSave: SerializedMisc = {
			lastUsedUrl: chosenUrl ?? misc.lastUsedUrl,
			lastUsedDownloadFolder: choosenFolder ?? misc.lastUsedDownloadFolder
		}
		await SaveSerializedMisc(miscToSave)
	}
	return (<Dialog open={dialogOpen} onOpenChange={dialogOpenStatusChangeRequest} modal={false}>
		<DialogContent>
			<DialogHeader>
				<DialogTitle>Add Download</DialogTitle>
				<DialogDescription>
					Add download using url
				</DialogDescription>
			</DialogHeader>
			<form className="grid grid-cols-3 gap-4">
				<Input className="col-span-3" onChange={(e) => {
					const eventSender = e.target;
					setChosenUrl(eventSender.value)

				}} type="url" placeholder="URL" defaultValue={misc.lastUsedUrl} />
				<Input className="col-span-2" type={"text"} value={choosenFolder ?? misc.lastUsedDownloadFolder} onChange={(e) => {
					const eventSender = e.target;
					setChoosenFolder(eventSender.value)
				}} />
				<Button className="col-start-3 bg-secondary" onClick={selectFolder} type="button">Select Folder</Button>
			</form>
			<DialogFooter>
				<Button type="submit" className="w-full" onClick={() => {
					if (chosenUrl === null || choosenFolder === null) {
						console.log("url or folder is null")
						console.log(chosenUrl, choosenFolder)
						return;
					}
					SaveMisc()
					submitEvent?.(chosenUrl, choosenFolder)
				}}>Add Download</Button>
			</DialogFooter>
		</DialogContent>
	</Dialog>)
}
