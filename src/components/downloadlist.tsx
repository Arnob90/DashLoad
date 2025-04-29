import React, { Children, useMemo, useRef, useState } from "react";
import { ReactNode } from "react";
import "../styles/white-image.scss"
import { DownloadInfo, DownloadInfoActions, PausedDownloadInfo, DownloadingInfo } from "../code/DownloadFromServer";
import { createColumnHelper, useReactTable, getCoreRowModel, flexRender } from "@tanstack/react-table";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { PauseIcon, PlayIcon, RotateCcw } from "lucide-react"
import { ContextMenu, ContextMenuTrigger, ContextMenuContent, ContextMenuItem } from "@/components/ui/context-menu";
import clsx from "clsx"
interface DownloadTableProps {
	downloadInfos: DownloadInfo[]
	className?: string
	pausedOrPlayButtonPressedEventHandler?: (info: DownloadInfo) => void;
	retryButtonPressedEventHandler?: (info: DownloadInfo) => void
	focusChangedEventHandler?: (info: DownloadInfo | null) => void
}
export function DownloadTable({ downloadInfos, pausedOrPlayButtonPressedEventHandler, retryButtonPressedEventHandler, focusChangedEventHandler }: DownloadTableProps) {
	const columnHelper = createColumnHelper<DownloadInfo>()
	const columns = useMemo(() => [
		columnHelper.accessor('filename', {
			header: 'Filename',
			cell: (info) => {
				const row = info.row.original;
				let requiredComponent: ReactNode = null;
				switch (row.type) {
					case "PausedDownloadInfo":
						requiredComponent = (
							<button onClick={() => pausedOrPlayButtonPressedEventHandler?.(row)}>
								<PlayIcon></PlayIcon>
							</button>
						)
						break
					case "DownloadingInfo":
						requiredComponent = (
							<button onClick={() => pausedOrPlayButtonPressedEventHandler?.(row)}>
								<PauseIcon></PauseIcon>
							</button>
						)
						break
					case "FailedDownloadInfo":
						requiredComponent = (
							<button onClick={() => retryButtonPressedEventHandler?.(row)}>
								<RotateCcw></RotateCcw>
							</button>
						)
				}
				return (
					<div className="flex gap-2 items-center" >
						{requiredComponent}
						{info.getValue()}
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
						const orig_row = row.original
						let focus_color = "focus:bg-primary/30"
						let pausedOrPlayStr = ""
						if (orig_row.type === "FailedDownloadInfo") {
							focus_color = "focus:bg-destructive/30"
						}
						if (orig_row.type === "SucceededDownloadInfo") {
							focus_color = "focus:bg-success/30"
						}
						if (orig_row.type === "PausedDownloadInfo") {
							pausedOrPlayStr = "Play"
						}
						else {
							pausedOrPlayStr = "Pause"
						}
						return <TableRow key={row.id} tabIndex={0} className={clsx("focus:outline-none", focus_color)} onFocus={() => focusChangedEventHandler?.(orig_row)} onBlur={() => focusChangedEventHandler?.(null)}>
							{
								row.getVisibleCells().map((cell) => {
									return <TableCell key={cell.id}>
										{flexRender(cell.column.columnDef.cell, cell.getContext())}
									</TableCell>
								})
							}
						</TableRow>
					})}
				</TableBody>
			</Table>
		</div >
	)

}
