import z from "zod"
import { useState } from "react"
import useWebSocket from "react-use-websocket"
export const browserDownloadStartRequestSchema = z.object(
	{
		url: z.string(),
	}
)

export type BrowserDownloadStartRequest = z.infer<typeof browserDownloadStartRequestSchema>


export function UseDownloadStartRequestQueue() {
	const socketUrl = "ws://127.0.0.1:8000/frontend/download/queue"
	const [url, setUrl] = useState<string | null>(null)
	const socket = useWebSocket(socketUrl, {
		onOpen: () => {
			console.log("Connected to " + socketUrl)
		},
		onMessage: (event) => {
			const parsed = browserDownloadStartRequestSchema.safeParse(JSON.parse(event.data))
			if (parsed.success) {
				setUrl(parsed.data.url)
			}
		}
	})
	return url
}
