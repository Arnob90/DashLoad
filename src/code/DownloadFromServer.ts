import { Header } from "@tanstack/react-table";
import { z } from "zod"

// 1. Base Schema corresponding to DownloadInfoState (excluding the 'type' field for now)
// Note: Pydantic's `None` typically maps to `null` in JSON.
const baseDownloadInfoSchema = z.object({
	download_id: z.string().nullable(), // str | None -> string | null
	filename: z.string().nullable(),    // str | None -> string | null
	filepath: z.string(),               // str -> string
	filesize: z.number().int().nullable(), // int | None -> integer | null
	last_url: z.string() //str -> string
});

// 2. Schema for DownloadingInfo
// Extends base and adds specific fields + the literal type discriminator
const downloadingInfoSchema = baseDownloadInfoSchema.extend({
	downloaded_file_portion: z.number().int().nullable(), // int | None -> integer | null
	type: z.literal('DownloadingInfo'), // Specific type value
	download_speed: z.number().nullable(),
});

// 3. Schema for PausedDownloadInfo
// It also has downloaded_file_portion according to the Pydantic model
// (Even though it's defined in DownloadingInfo, PausedDownloadInfo also declares it)
const pausedDownloadInfoSchema = baseDownloadInfoSchema.extend({
	downloaded_file_portion: z.number().int().nullable(), // int | None -> integer | null
	type: z.literal('PausedDownloadInfo'), // Specific type value
});

// 4. Schema for FailedDownloadInfo
// Extends base and adds the literal type discriminator
const failedDownloadInfoSchema = baseDownloadInfoSchema.extend({
	type: z.literal('FailedDownloadInfo'), // Specific type value
	// Add any other fields specific to failed state if they exist in practice
	// e.g., error_message: z.string().optional()
});

// 5. Schema for SucceededDownloadInfo
// Extends base and adds the literal type discriminator
const succeededDownloadInfoSchema = baseDownloadInfoSchema.extend({
	type: z.literal('SucceededDownloadInfo'), // Specific type value
	// Add any other fields specific to succeeded state if they exist in practice
	// e.g., final_size: z.number().int().optional() (if different from filesize)
});


const pendingDownloadInfo = baseDownloadInfoSchema.extend({
	type: z.literal('PendingDownloadInfo'),
});
const queuedDownloadInfo = baseDownloadInfoSchema.extend({
	type: z.literal('QueuedDownloadInfo')
})

// 6. Create the Discriminated Union
// Zod uses the 'type' field to determine which schema to apply
export const downloadInfoUnionSchema = z.discriminatedUnion('type', [
	downloadingInfoSchema,
	pausedDownloadInfoSchema,
	failedDownloadInfoSchema,
	succeededDownloadInfoSchema,
	pendingDownloadInfo,
	queuedDownloadInfo
]);

// 7. Create the final schema for the API response (a list/array of the union)
export const downloadsListSchema = z.array(downloadInfoUnionSchema);


// --- Optional: Infer TypeScript types from the schemas ---

// Type for a single download info object (could be any of the states)
export type DownloadInfo = z.infer<typeof downloadInfoUnionSchema>;

// Type for the specific states
export type DownloadingInfo = z.infer<typeof downloadingInfoSchema>;
export type PausedDownloadInfo = z.infer<typeof pausedDownloadInfoSchema>;
export type FailedDownloadInfo = z.infer<typeof failedDownloadInfoSchema>;
export type SucceededDownloadInfo = z.infer<typeof succeededDownloadInfoSchema>;
export type PendingDownloadInfo = z.infer<typeof pendingDownloadInfo>
export type QueuedDownloadInfo = z.infer<typeof queuedDownloadInfo>

// Type for the entire API response array
export type DownloadsList = z.infer<typeof downloadsListSchema>;
// export interface DownloadInfo {
// 	download_id: string | null
// 	filesize: number | null
// 	downloaded_file_portion: number | null
// 	filename: string | null
// 	filepath: string
// }
interface Headers {
	Accept: string,
	'Content-Type': string
}
interface HeadersWithSecret extends Headers {
	'x-session-token': string
}
export class DefaultRequestOpts {
	// Will soon be made private as uuidless use is deprecated
	static headers: Headers = {
		'Accept': 'application/json',
		'Content-Type': 'application/json'
	}
	fullHeaders: HeadersWithSecret
	public constructor(secret: string) {
		this.fullHeaders = {
			...DefaultRequestOpts.headers,
			'x-session-token': secret

		}
	}
}
export class DownloadInfoActions {
	static getDownloadProgress(givenInfo: DownloadingInfo | PausedDownloadInfo): number | null {
		if (givenInfo.downloaded_file_portion === null || givenInfo.filesize === null) {
			return null
		}
		return (givenInfo.downloaded_file_portion / givenInfo.filesize) * 100
	}
	static getSizeInMIB(givenSize: number) {
		return parseFloat((givenSize / (2 ** 20)).toFixed(1))
	}
}
