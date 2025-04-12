import React, { Children, useMemo, useRef, useState } from "react";
import { ReactNode } from "react";
import "../styles/white-image.scss"
import Result from "postcss/lib/result";
import { DownloadInfo, DownloadInfoActions } from "../code/DownloadFromServer";
import { ColumnDef, createColumnHelper, useReactTable, getCoreRowModel, flexRender } from "@tanstack/react-table";
import { DataTable } from "@/components/ui/data-table";
import { Pause, Play } from "lucide-react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
interface DownloadTableProps {
	downloadInfos: DownloadInfo[]
	className?: string
}
export function DownloadTable({ downloadInfos, className }: DownloadTableProps) {
	const columnHelper = createColumnHelper<DownloadInfo>()
	const columns = useMemo(() => [
		columnHelper.accessor('filename', {
			header: 'Filename',
			cell: info =>
				<div className="flex items-center gap-2">
					<img src="../../assets/pause-button.svg" className="w-10 h-10" />
					{info.getValue()}
				</div>
				?? '—',
		}),
		columnHelper.accessor('downloaded_file_portion', {
			header: 'Downloaded',
			cell: info => {
				const value = info.getValue();
				return value !== null ? `${DownloadInfoActions.getSizeInMIB(value as number)} MIB` : '—';
			},
		}),
		columnHelper.accessor('filesize', {
			header: 'Filesize',
			cell: info => info.getValue() !== null ? `${DownloadInfoActions.getSizeInMIB(info.getValue() as number)} MIB` : '—',
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
						return <TableRow key={row.id} tabIndex={0} className="focus:outline-none focus:bg-primary/30">
							{row.getVisibleCells().map((cell) => {
								return <TableCell key={cell.id}>
									{flexRender(cell.column.columnDef.cell, cell.getContext())}
								</TableCell>
							})}
						</TableRow>
					})}
				</TableBody>
			</Table>
		</div>
	)

}
