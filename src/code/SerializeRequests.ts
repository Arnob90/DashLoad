import z from "zod"

export const serialize_request_schema = z.object({
	filepath_to_serialize_to: z.string(),
})

export const deserialize_request_schema = z.object({
	filepath_to_deserialize_from: z.string(),
})
export type SerializeRequest = z.infer<typeof serialize_request_schema>
export type DeserializeRequest = z.infer<typeof deserialize_request_schema>
