/**
 * Base adapter interface for ATS detection and form filling
 */
import { Page } from 'playwright';

export interface FieldMapping {
  canonical_field: string;
  selector: string;
  type: 'input' | 'select' | 'textarea' | 'radio' | 'checkbox';
  label?: string;
}

export interface DetectionResult {
  ats_type: string;
  confidence: number;
  indicators: string[];
}

export interface FillResult {
  field_name: string;
  value: string;
  success: boolean;
  error?: string;
}

export abstract class ATSAdapter {
  /**
   * Detect if this adapter can handle the current page
   */
  abstract detect(page: Page): Promise<DetectionResult>;

  /**
   * Collect form fields from the page
   */
  abstract collectFields(page: Page): Promise<FieldMapping[]>;

  /**
   * Fill form fields with provided data
   */
  abstract fill(
    page: Page,
    data: Record<string, any>
  ): Promise<FillResult[]>;

  /**
   * Attach resume/CV file
   */
  abstract attachResume(page: Page, filepath: string): Promise<boolean>;

  /**
   * Take screenshot of current state
   */
  async snapshot(page: Page, path: string): Promise<string> {
    await page.screenshot({ path, fullPage: true });
    return path;
  }

  /**
   * Common helper: Find input by various strategies
   */
  protected async findInputByLabel(
    page: Page,
    labels: string[]
  ): Promise<string | null> {
    for (const label of labels) {
      // Try by label text
      const byLabel = await page.locator(`label:has-text("${label}")`).first();
      if (await byLabel.count() > 0) {
        const forAttr = await byLabel.getAttribute('for');
        if (forAttr) return `#${forAttr}`;
      }

      // Try by placeholder
      const byPlaceholder = await page.locator(`input[placeholder*="${label}" i]`).first();
      if (await byPlaceholder.count() > 0) {
        return `input[placeholder*="${label}" i]`;
      }

      // Try by name attribute
      const byName = await page.locator(`input[name*="${label.toLowerCase()}" i]`).first();
      if (await byName.count() > 0) {
        return `input[name*="${label.toLowerCase()}" i]`;
      }

      // Try by aria-label
      const byAria = await page.locator(`input[aria-label*="${label}" i]`).first();
      if (await byAria.count() > 0) {
        return `input[aria-label*="${label}" i]`;
      }
    }

    return null;
  }
}
