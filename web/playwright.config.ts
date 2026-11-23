import { defineConfig, devices } from "@playwright/test";

// Testa o build estático (out/) servido localmente, como no GitHub Pages.
export default defineConfig({
  testDir: "tests/e2e",
  fullyParallel: true,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? "github" : "list",
  use: { baseURL: "http://localhost:4175", trace: "retain-on-failure" },
  projects: [
    { name: "mobile", use: { ...devices["Pixel 7"], viewport: { width: 390, height: 844 } } },
    { name: "web", use: { ...devices["Desktop Chrome"], viewport: { width: 1440, height: 900 } } },
  ],
  webServer: {
    command: "node scripts/serve.mjs out 4175",
    url: "http://localhost:4175",
    reuseExistingServer: !process.env.CI,
  },
});
