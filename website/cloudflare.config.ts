import { defineConfig } from "cf/config";

export default defineConfig({
	worker: {
		name: "ha-webos-remote-site",
		compatibilityDate: "2026-10-13",
		workersDev: false,
		previewUrls: false,
		observability: {
			enabled: true,
			traces: {
				enabled: true,
				headSamplingRate: 0.01,
			},
		},
		assets: {
			notFoundHandling: "none",
		},
		domains: [
			"webos.royjen.com",
		],
	},
});
