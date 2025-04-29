import z from "zod"
const serializedMiscSchema = z.object({
	lastUsedUrl: z.string(),
	lastUsedDownloadFolder: z.string()
})
export type SerializedMisc = z.infer<typeof serializedMiscSchema>
export async function GetSerializedMisc(): Promise<SerializedMisc> {
	const gottenMisc = await window.electronApi.getMiscJson();
	console.log(gottenMisc)
	if (gottenMisc === null || gottenMisc === undefined) {
		return {
			lastUsedUrl: "",
			lastUsedDownloadFolder: ""
		}
	}
	const gottenMiscParsed: SerializedMisc = serializedMiscSchema.parse(gottenMisc);
	return gottenMiscParsed;
}
export async function SaveSerializedMisc(givenMisc: SerializedMisc): Promise<void> {
	await window.electronApi.saveMiscJson(givenMisc);
}
