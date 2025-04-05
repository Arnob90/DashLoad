import React from "react";
import { Button, buttonVariants } from "../components/ui/button";
import { Progress } from "@/components/ui/progress"
import "./styles/globals.css"
import "./styles/white-image.scss"
import { DownloadItem, DownloadInfo, DownloadList } from "./components/downloadlist";
import { ScrollArea } from "@/components/ui/scroll-area"
import { AddDownloadDialogButton } from "./components/AddDownloadDialog";
export default function App() {
	return (
		<div className="grid grid-cols-1">
			<div className="flex flex-col">
				<div className="flex w-full py-2 border-2 border-b-gray-600 sticky">
					<AddDownloadDialogButton className="mx-3">
						<div className="w-15 h-15 mx-2 bg-primary p-4">
							<img className="white-svg" src="../assets/plusicon.svg" />
						</div>
					</AddDownloadDialogButton>

				</div>
				<DownloadList>
					<DownloadItem filename="Hollow Knight Silksong" filesize={80} progress={20}></DownloadItem>
				</DownloadList>
			</div>
		</div>
	)
}
