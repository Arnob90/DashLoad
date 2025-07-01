import { z } from "zod";
export const fastapiValidationErrorSchema = z.object({
	detail: z.string()
})


