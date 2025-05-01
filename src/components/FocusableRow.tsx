import React from "react";
import { ReactNode } from "react";
import { TableHeader, TableRow } from "@/components/ui/table";
export interface FocusableRowProps {
	focusClassesMaybe?: string
	children: ReactNode
	normalClassesMaybe?: string
	focused: boolean
	onClick?: () => void
}
export default function FocusableRow({ focusClassesMaybe, focused, children, normalClassesMaybe, onClick }: FocusableRowProps) {
	const focusClasses = focusClassesMaybe ?? ""
	const normalClasses = normalClassesMaybe ?? ""
	return (
		<TableRow className={focused ? focusClasses : normalClasses} onClick={onClick}>
			{children}
		</TableRow >
	)
}
