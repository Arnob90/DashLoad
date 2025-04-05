import React, { Children, useRef, useState } from "react";
import { ReactNode } from "react";
import { Progress } from "@/components/ui/progress"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator";
import { Grid } from "@radix-ui/themes"
import "../styles/white-image.scss"
export interface DownloadInfo {
	filename: string;
	progress: number;
	filesize: number;
}
export function DownloadItem({ filename, progress, filesize }: DownloadInfo) {
	return (
		<div className="flex justify-stretch w-full">
			<label className="text-lg mx-3">{filename}</label>
			<label className="text-lg">{filesize}MB</label>
		</div>
	)
}
interface DownloadListProps {
	children: ReactNode;
}
interface DownloadListContainerProps {
	children: ReactNode;
	className?: string
}
function DownloadListContainer({ children, className }: DownloadListContainerProps) {
	return (
		<ul className={`my-2 border-2 border-gray-500 min-h-96 ${className ?? ''}`}>
			{children}
		</ul>
	)
}
export function DownloadList({ children }: DownloadListProps) {
	const [focusedIndex, setFocusedIndex] = useState(-1);
	const childrenList: ReactNode[] = React.Children.toArray(children);
	return (
		<DownloadListContainer className="mx-5">
			{

				childrenList.map((node, i) => {
					return (
						<li tabIndex={0} onFocus={() => setFocusedIndex(i)} onBlur={() => { setFocusedIndex(-1) }} className={`flex flex-row ${focusedIndex != i ? "outline-bottom" : ""} focus:outline outline-gray-500 focus:outline-primary justify-between`}>
							{node}
						</li>
					)
				})
			}
		</DownloadListContainer >
	)
}
