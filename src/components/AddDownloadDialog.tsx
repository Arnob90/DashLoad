import React, { Children } from "react";
import { ReactNode } from "react";
import { DialogHeader, DialogTrigger, DialogTitle, DialogDescription, DialogContent, Dialog } from "@/components/ui/dialog";
interface AddDownloadDialogButtonProps {
	children: ReactNode
	className?: string
}
export function AddDownloadDialogButton({ children, className }: AddDownloadDialogButtonProps) {
	return (<Dialog>
		<DialogTrigger className={className ?? ""}>{children}</DialogTrigger>
		<DialogContent>
			<DialogHeader>
				<DialogTitle>Are you absolutely sure?</DialogTitle>
				<DialogDescription>
					This action cannot be undone. This will permanently delete your account
					and remove your data from our servers.
				</DialogDescription>
			</DialogHeader>
		</DialogContent>
	</Dialog>)
}
