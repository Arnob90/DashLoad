import React, { useCallback } from "react";
import { useEffect } from "react"
export function useKeyHandler(key: string, callback: () => void) {

	const handleKeyPress = useCallback((e: KeyboardEvent) => {
		if (e.key === key) {
			callback()
		}
	}, [key, callback])
	useEffect(() => {
		document.addEventListener("keydown", handleKeyPress)
		return () => {
			document.removeEventListener("keydown", handleKeyPress)
		}
	}, [key])
}
