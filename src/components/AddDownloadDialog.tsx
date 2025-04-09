import React, { Children, useEffect, useState } from "react";
import { ReactNode } from "react";
import { DialogHeader, DialogTrigger, DialogTitle, DialogDescription, DialogContent, Dialog, DialogFooter } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
interface AddDownloadDialogButtonProps {
	children: ReactNode
	className?: string
	submitEvent?: (url: string, folderPath: string) => void;
}
export function AddDownloadDialogButton({ children, className, submitEvent: folderChoosenEvent }: AddDownloadDialogButtonProps) {
	const [selectedFolder, setSelectedFolder] = useState("")
	const [selectedUrl, setSelectedUrl] = useState("")
	async function handleOpenFileDialog() {
		const fileDialogResult = window.electronApi.promptToSelectDir();
		fileDialogResult.then((choosen) => {
			if (choosen.canceled) {
				return
			}
			const choosenFolders = choosen.filePaths;
			if (choosenFolders.length != 1) {
				console.error("Huh! Selecting more than one folder should be impossible. Continuing for gradual degradation")
			}
			const selectedPath = choosenFolders[0]
			setSelectedFolder(selectedPath)
		})
	}
	return (<Dialog>
		<DialogTrigger className={className ?? ""}>{children}</DialogTrigger>
		<DialogContent>
			<DialogHeader>
				<DialogTitle>Add Download</DialogTitle>
				<DialogDescription>
					Add download using url
				</DialogDescription>
			</DialogHeader>
			<div className="grid grid-cols-3 gap-4">
				<Input className="col-span-4" onChange={(e) => {
					const eventSender = e.target;
					const text = eventSender.value;
					setSelectedUrl(text);
				}} type="url" placeholder="URL" />
				<div className="border-2 border-background-lighter col-start-1 col-span-3 rounded-md">
					<Label title={selectedFolder}>{selectedFolder}</Label>
				</div>
				<Button className="col-start-4" onClick={() => {
					handleOpenFileDialog()
				}}>Select Folder</Button>
			</div>
			<DialogFooter>
				<Button type="submit" className="w-full" onClick={() => {
					if (folderChoosenEvent) {
						folderChoosenEvent(selectedUrl, selectedFolder);
					}
				}}>Add Download</Button>
			</DialogFooter>
		</DialogContent>
	</Dialog>)
}
