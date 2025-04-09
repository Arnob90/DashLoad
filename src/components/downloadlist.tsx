import React, { Children, useRef, useState } from "react";
import { ReactNode } from "react";
import { Progress } from "@/components/ui/progress"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator";
import { Grid } from "@radix-ui/themes"
import "../styles/white-image.scss"
import Result from "postcss/lib/result";
export interface DownloadItemProps {
	filename: string;
	progress: number;
	filesize: number | null;
	completedSize: number;
}
export function DownloadItem({ filename, completedSize, filesize }: DownloadItemProps) {
	console.log(completedSize)
	return (
		<>
			<label className="text-lg mx-3">{filename}</label>
			<label className="text-lg">{completedSize} MIB</label>
			<label className="text-lg">{filesize ?? "Unknown"} MB</label>
		</>
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
		<div className={`my-2 border-2 border-gray-500 min-h-96 ${className ?? ''}`}>
			{children}
		</div>
	)
}
interface BackgroundGridProps {

	children: ReactNode;
}
export function BackgroundGrid({ children }: BackgroundGridProps) {
	const childrenList = React.Children.toArray(children);
	if (childrenList.length == 0) {
		return <div className="bg-gray-900">
		</div>;
	}
	const firstElem = childrenList[0]
	const rest = childrenList.slice(1)
	return (
		<>
			<div className="bg-black border-b-gray-500 outline-2 outline-gray-500">
				{firstElem}
			</div>
			{rest.map((child) => {
				return (
					<div className="bg-black border-l-2 border-b-gray-500 outline-2 outline-gray-500">
						<div className="mx-1">
							{child}
						</div>
					</div>
				)
			})}
		</>
	)
}
export function DownloadList({ children }: DownloadListProps) {
	const [focused, setFocus] = useState(-1)
	const childrenArr = React.Children.toArray(children)
	return (
		<DownloadListContainer>
			<div className="grid grid-cols-3 max-w-full">
				<BackgroundGrid>
					<label>Filename</label>
					<label>Completed Size</label>
					<label>Filesize</label>
				</BackgroundGrid>
			</div>
			{childrenArr.map((elem, i) => {
				return (
					<div tabIndex={0} onFocus={() => { setFocus(i) }} onBlur={() => { setFocus(-1) }} className={`grid grid-cols-3 justify-stretch focus:outline-2 focus:outline-primary ${focused != i ? "outline-bottom" : ""}`}>
						{elem}
					</div>
				)
			})}
		</DownloadListContainer>
	)
}
