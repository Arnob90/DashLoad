import { Dialog, DialogTrigger, DialogHeader, DialogContent, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import React, { ReactNode, useRef, useState } from "react"
interface DownloadDeleteDialogProps {
	children: ReactNode
	deleteConfirmationCallback?: (deleteLocalFile: boolean) => void
}
export function DownloadDeleteDialog({ children, deleteConfirmationCallback }: DownloadDeleteDialogProps) {
	const [deleteLocalFileAsWell, setDeleteLocalFileAsWell] = useState(false)
	const [dialogOpen, setDialogOpen] = useState(false)
	return (
		<Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
			<DialogTrigger asChild>
				{children}
			</DialogTrigger>
			<DialogContent>
				<DialogHeader>
					<DialogTitle>Delete Download</DialogTitle>
					<DialogDescription>
						Are you sure you want to delete the item?
					</DialogDescription>
					<p>This action cannot be undone</p>
				</DialogHeader>
				<div className="flex flex-row gap-3">
					<Checkbox onCheckedChange={(checked) => {
						if (checked === "indeterminate") {
							setDeleteLocalFileAsWell(false)
						}
						const checkedStatus = checked.valueOf() as boolean
						setDeleteLocalFileAsWell(checkedStatus)
					}} />
					<Label className="text-red-400">Delete File on Disk</Label>
				</div>
				<DialogFooter>
					<Button variant={"destructive"} onClick={() => { deleteConfirmationCallback?.(deleteLocalFileAsWell); setDialogOpen(false) }}>Delete</Button>
				</DialogFooter>
			</DialogContent>
		</Dialog >
	)
}
