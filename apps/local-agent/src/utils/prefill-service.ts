/**
 * Prefill service - orchestrates the browser automation
 */
import { chromium, Browser, Page } from 'playwright';
import { AdapterFactory } from '../adapters';
import { ApiClient, PrefillIntent, PrefillLog } from './api-client';
import path from 'path';
import fs from 'fs';

export class PrefillService {
  private browser: Browser | null = null;
  private apiClient: ApiClient;
  private adapterFactory: AdapterFactory;
  private screenshotsDir: string;
  private stopBeforeSubmit: boolean;

  constructor(
    apiClient: ApiClient,
    screenshotsDir: string = './screenshots',
    stopBeforeSubmit: boolean = true
  ) {
    this.apiClient = apiClient;
    this.adapterFactory = new AdapterFactory();
    this.screenshotsDir = screenshotsDir;
    this.stopBeforeSubmit = stopBeforeSubmit;

    // Ensure screenshots directory exists
    if (!fs.existsSync(screenshotsDir)) {
      fs.mkdirSync(screenshotsDir, { recursive: true });
    }
  }

  /**
   * Initialize browser
   */
  async initBrowser(headless: boolean = false): Promise<void> {
    this.browser = await chromium.launch({
      headless,
      args: ['--start-maximized'],
    });
  }

  /**
   * Close browser
   */
  async closeBrowser(): Promise<void> {
    if (this.browser) {
      await this.browser.close();
      this.browser = null;
    }
  }

  /**
   * Execute a prefill intent
   */
  async executePrefill(intentId: string, authToken: string): Promise<void> {
    const startTime = Date.now();
    let page: Page | null = null;

    try {
      // Fetch intent from API
      console.log(`Fetching intent ${intentId}...`);
      const intent = await this.apiClient.fetchIntent(intentId, authToken);

      if (!this.browser) {
        throw new Error('Browser not initialized');
      }

      // Create new page
      const context = await this.browser.newContext({
        viewport: { width: 1920, height: 1080 },
      });
      page = await context.newPage();

      // Navigate to job URL
      console.log(`Navigating to ${intent.job_url}...`);
      await page.goto(intent.job_url, { waitUntil: 'networkidle' });

      // Take initial screenshot
      const screenshotPaths: string[] = [];
      const initialScreenshot = path.join(
        this.screenshotsDir,
        `${intentId}_01_initial.png`
      );
      await page.screenshot({ path: initialScreenshot, fullPage: true });
      screenshotPaths.push(initialScreenshot);

      // Detect ATS type
      console.log('Detecting ATS type...');
      const { adapter, detection } = await this.adapterFactory.detectAdapter(page);
      console.log(`Detected: ${detection.ats_type} (confidence: ${detection.confidence})`);

      // Collect and fill fields
      console.log('Filling form fields...');
      const fillResults = await adapter.fill(page, intent.user_fields);

      // Take screenshot after filling
      const filledScreenshot = path.join(
        this.screenshotsDir,
        `${intentId}_02_filled.png`
      );
      await page.screenshot({ path: filledScreenshot, fullPage: true });
      screenshotPaths.push(filledScreenshot);

      // Attach resume if available
      let resumeAttached = false;
      const resumePath = intent.attachments.resume;
      
      if (resumePath && fs.existsSync(resumePath)) {
        console.log('Attaching resume...');
        resumeAttached = await adapter.attachResume(page, resumePath);
        
        if (resumeAttached) {
          // Take screenshot after resume attachment
          const resumeScreenshot = path.join(
            this.screenshotsDir,
            `${intentId}_03_resume_attached.png`
          );
          await page.screenshot({ path: resumeScreenshot, fullPage: true });
          screenshotPaths.push(resumeScreenshot);
        }
      }

      // Create log
      const duration = (Date.now() - startTime) / 1000;
      const log: PrefillLog = {
        intent_id: intentId,
        detected_ats: detection.ats_type,
        detection_confidence: detection.confidence,
        filled_fields: fillResults,
        missing_fields: this.extractMissingFields(intent.user_fields, fillResults),
        errors: this.extractErrors(fillResults),
        resume_attached: resumeAttached,
        attachment_errors: resumeAttached ? [] : ['Resume not attached'],
        screenshot_paths: screenshotPaths,
        timestamp: new Date().toISOString(),
        duration_seconds: duration,
        stopped_before_submit: this.stopBeforeSubmit,
        field_mappings: {},
      };

      // Report result to API
      console.log('Reporting result to API...');
      await this.apiClient.reportResult(intentId, authToken, log);

      console.log('Prefill completed successfully!');
      console.log(`- Fields filled: ${fillResults.filter(r => r.success).length}/${fillResults.length}`);
      console.log(`- Resume attached: ${resumeAttached}`);
      console.log(`- Screenshots: ${screenshotPaths.length}`);

      // Keep browser open if not headless (for user review)
      if (!this.stopBeforeSubmit) {
        console.log('WARNING: Auto-submit is disabled. Browser will remain open.');
      }

      // Wait a bit before closing
      await page.waitForTimeout(2000);

    } catch (error) {
      console.error('Error during prefill:', error);
      
      // Try to report error
      try {
        const duration = (Date.now() - startTime) / 1000;
        const errorLog: PrefillLog = {
          intent_id: intentId,
          detected_ats: 'unknown',
          detection_confidence: 0,
          filled_fields: [],
          missing_fields: [],
          errors: [{ field: 'general', error_message: error instanceof Error ? error.message : 'Unknown error' }],
          resume_attached: false,
          attachment_errors: [],
          screenshot_paths: [],
          timestamp: new Date().toISOString(),
          duration_seconds: duration,
          stopped_before_submit: true,
          field_mappings: {},
        };

        await this.apiClient.reportResult(intentId, authToken, errorLog);
      } catch (reportError) {
        console.error('Failed to report error:', reportError);
      }
      
      throw error;
    } finally {
      if (page) {
        await page.close();
      }
    }
  }

  /**
   * Extract missing fields from fill results
   */
  private extractMissingFields(
    requestedFields: Record<string, any>,
    results: Array<{ field_name: string; success: boolean }>
  ): string[] {
    const filledFields = new Set(
      results.filter(r => r.success).map(r => r.field_name)
    );
    
    return Object.keys(requestedFields).filter(
      field => !filledFields.has(field)
    );
  }

  /**
   * Extract errors from fill results
   */
  private extractErrors(
    results: Array<{ field_name: string; success: boolean; error?: string }>
  ): Array<{ field: string; error_message: string }> {
    return results
      .filter(r => !r.success && r.error)
      .map(r => ({
        field: r.field_name,
        error_message: r.error || 'Unknown error',
      }));
  }
}
