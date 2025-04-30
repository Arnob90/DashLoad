import React from "react";
import { ReactNode } from "react";
import { TableHeader, TableRow } from "@/components/ui/table";
export interface FocusableRowProps {
	focusClassesMaybe?: string
	children: ReactNode
	normalClassesMaybe?: string
	key?: React.Key
	focused: boolean
	onClick?: () => void
}
export default function FocusableRow({ focusClassesMaybe, focused, children, normalClassesMaybe, key, onClick }: FocusableRowProps) {
	const focusClasses = focusClassesMaybe ?? ""
	const normalClasses = normalClassesMaybe ?? ""
	return (
		<TableRow className={focused ? focusClasses : normalClasses} key={key} onClick={onClick}>
			{children}
		</TableRow >
	)
}
