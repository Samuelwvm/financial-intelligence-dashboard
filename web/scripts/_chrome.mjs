import { chromium } from "@playwright/test";
const b = await chromium.launch({ args: ["--remote-debugging-port=9333"], headless: true });
console.log("chrome pronto"); setTimeout(() => b.close(), 600000);
