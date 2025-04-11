import React, { Children, useMemo, useRef, useState } from "react";
import { ReactNode } from "react";
import "../styles/white-image.scss"
import Result from "postcss/lib/result";
import { DownloadInfo, DownloadInfoActions } from "../code/DownloadFromServer";
import { ColumnDef, createColumnHelper, useReactTable, getCoreRowModel } from "@tanstack/react-table";
import { DataTable } from "@/components/ui/data-table";
interface DownloadTableProps {
	downloadInfos: DownloadInfo[]
	className?: string
}
export function DownloadTable({ downloadInfos, className }: DownloadTableProps) {
	const columnHelper = createColumnHelper()
	const columns = useMemo(() => [
		columnHelper.accessor('filename', {
			header: 'Filename',
			cell: info => info.getValue() ?? '—',
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
		<DataTable columns={columns} data={downloadInfos} className={className}></DataTable>
	)

}
