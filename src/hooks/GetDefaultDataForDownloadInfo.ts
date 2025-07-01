import { GetSerializedMisc, SerializedMisc } from "../code/MiscObj";
import { UseDownloadStartRequestQueue } from "./BrowserDownloadStartRequest";
import { useEffect, useState } from "react";
export function UseDefaultDataForDownloadDialog() {
	const [defaultData, setDefaultData] = useState<SerializedMisc>({ lastUsedUrl: "", lastUsedDownloadFolder: "" })
	const queuedUrl = UseDownloadStartRequestQueue()
	useEffect(() => {
		(async () => {
			const gottenMisc = await GetSerializedMisc()
			setDefaultData(gottenMisc)
		})()
	}, [])
	useEffect(() => {
		setDefaultData((prev) => {
			return {
				...prev,
				lastUsedUrl: queuedUrl ?? prev.lastUsedUrl,
			}
		}
		)
	}, [queuedUrl])
	return defaultData
}
