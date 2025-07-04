import React, { useEffect, useMemo, useRef, useState } from "react";
import FocusableRow from "./FocusableRow";
import { ReactNode } from "react";
import "../styles/white-image.scss"
import { DownloadInfo, DownloadInfoActions } from "../code/DownloadFromServer";
import { createColumnHelper, useReactTable, getCoreRowModel, flexRender } from "@tanstack/react-table";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { PauseIcon, PlayIcon, RotateCcw } from "lucide-react"
import { ContextMenu, ContextMenuTrigger, ContextMenuContent, ContextMenuItem } from "@/components/ui/context-menu"
import clsx from "clsx"
import { Button } from "@radix-ui/themes";
import { useKeyHandler } from "../hooks/KeyHandler";
import { Label } from "@/components/ui/label";
interface DownloadTableProps {
	downloadInfos: DownloadInfo[]
	className?: string
	pausedOrPlayButtonPressedEventHandler?: (info: DownloadInfo) => void;
	retryButtonPressedEventHandler?: (info: DownloadInfo) => void
	focusChangedEventHandler?: (info: DownloadInfo | null) => void
}
export function DownloadTable({ downloadInfos, pausedOrPlayButtonPressedEventHandler, retryButtonPressedEventHandler, focusChangedEventHandler }: DownloadTableProps) {

	const [focusedRow, setFocusedRow] = useState<DownloadInfo | null>(null)
	function setFocus(info: DownloadInfo | null) {
		console.log(focusedRow)
		setFocusedRow(info)
		focusChangedEventHandler?.(info)
	}
	useKeyHandler("Escape", () => {
		setFocus(null)
	})
	const columnHelper = createColumnHelper<DownloadInfo>()
	const columns = useMemo(() => [
		columnHelper.accessor('filename', {
			header: 'Filename',
			cell: (info) => {
				const row = info.row.original;
				let placeHolderValueIfRowEmpty: string = "Lorem Ipsum"
				let requiredComponent: ReactNode = null;
				if (row.type == "PausedDownloadInfo") {
					requiredComponent = (
						<button onClick={() => pausedOrPlayButtonPressedEventHandler?.(row)}>
							<PlayIcon></PlayIcon>
						</button>
					)
				}
				else if (row.type == "DownloadingInfo" || row.type == "PendingDownloadInfo") {
					requiredComponent = (
						<button onClick={() => pausedOrPlayButtonPressedEventHandler?.(row)}>
							<PauseIcon></PauseIcon>
						</button>
					)
				}
				else if (row.type == "FailedDownloadInfo") {
					requiredComponent = (
						<button onClick={() => retryButtonPressedEventHandler?.(row)}>
							<RotateCcw></RotateCcw>
						</button>
					)
				}
				else if (row.type == "QueuedDownloadInfo") {
					requiredComponent = null
					placeHolderValueIfRowEmpty = row.last_url
				}
				return (
					<div className="flex gap-2 items-center" >
						{requiredComponent}
						<Label className="text-ellipsis">{info.getValue() ?? placeHolderValueIfRowEmpty}</Label>
					</div >
				)
			}
		}),
		columnHelper.accessor('type', {
			header: 'Status',
			cell: (info) => {
				const main_info = info.row.original
				switch (main_info.type) {
					case "DownloadingInfo":
						return <p>Downloading</p>
					case "PausedDownloadInfo":
						return <p>Paused</p>
					case "FailedDownloadInfo":
						return <p>Failed</p>
					case "SucceededDownloadInfo":
						return <p>Succeeded</p>
					case "QueuedDownloadInfo":
						return <p>Waiting for internet...</p>
					case "PendingDownloadInfo":
						return <p>Waiting for internet...</p>
					default:
						return <p>-</p>
				}
			}
		}),
		columnHelper.accessor('downloaded_file_portion', {
			header: 'Downloaded',
			cell: info => {
				const value = info.getValue();
				return value !== null && value !== undefined ? `${DownloadInfoActions.getSizeInMIB(value as number)} MIB` : '—';
			},
		}),
		columnHelper.accessor('download_speed', {
			header: 'Download Speed',
			cell: (info) => {
				const main_info = info.row.original
				switch (main_info.type) {
					case "DownloadingInfo":
						return <p>{main_info.download_speed !== null && main_info.download_speed !== undefined ? `${main_info.download_speed.toFixed(2)} MB/S` : "-"}</p>
					default:
						return <p>-</p>
				}
			},
		}),
		columnHelper.accessor('filesize', {
			header: 'Filesize',
			cell: info => info.getValue() !== null && info.getValue() !== undefined ? `${DownloadInfoActions.getSizeInMIB(info.getValue() as number)} MIB` : '—',
		}),
	], []);
	const table = useReactTable({
		data: downloadInfos,
		columns: columns,
		getCoreRowModel: getCoreRowModel()
	})
	return (
		<div className="p-2">
			<Table>
				<TableHeader>
					{table.getHeaderGroups().map((headerGroup) => {
						return (
							<TableRow key={headerGroup.id} className="">
								{headerGroup.headers.map((header) =>
									<TableHead key={header.id}>
										{header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
									</TableHead>
								)}
							</TableRow>
						)
					})}
				</TableHeader>
				<TableBody>
					{table.getRowModel().rows.map((row) => {
						const origRow = row.original
						let focusColor = "bg-primary/30"
						let pausedOrPlayStr = ""
						if (origRow.type === "FailedDownloadInfo") {
							focusColor = "bg-destructive/30"
						}
						if (origRow.type === "SucceededDownloadInfo") {
							focusColor = "bg-success/30"
						}
						if (origRow.type === "PausedDownloadInfo") {
							pausedOrPlayStr = "Play"
						}
						else {
							pausedOrPlayStr = "Pause"
						}
						return (
							<FocusableRow key={row.id} focusClassesMaybe={focusColor} focused={origRow.download_id === focusedRow?.download_id} onClick={() => { setFocus(origRow) }}>
								{
									row.getVisibleCells().map((cell) => {
										return <TableCell key={cell.id}>
											{flexRender(cell.column.columnDef.cell, cell.getContext())}
										</TableCell>
									})
								}
							</FocusableRow>
						)
					})}
				</TableBody>
			</Table>
		</div >
	)

}
