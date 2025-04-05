import React from "react"
interface ProgressBarProps {
	filledPercent: number;
}
export function CircularProgressBar({ filledPercent }: ProgressBarProps) {
	return (
		<svg viewBox="0 0 100 100">
			<circle radius={50} cx={50} cy={50}></circle>
		</svg>
	)
}
