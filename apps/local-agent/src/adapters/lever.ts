/**
 * Lever ATS Adapter
 */
import { Page } from 'playwright';
import { ATSAdapter, DetectionResult, FieldMapping, FillResult } from './base';

export class LeverAdapter extends ATSAdapter {
  async detect(page: Page): Promise<DetectionResult> {
    const indicators: string[] = [];
    let confidence = 0;

    // Check for Lever-specific elements
    const hasLeverBranding = await page.locator('a[href*="lever.co"]').count() > 0;
    if (hasLeverBranding) {
      indicators.push('lever.co link found');
      confidence += 0.4;
    }

    // Check URL patterns
    const url = page.url();
    if (url.includes('jobs.lever.co')) {
      indicators.push('Lever URL pattern');
      confidence += 0.5;
    }

    // Check for Lever form class patterns
    const hasLeverForm = await page.locator('.application-form, .lever-form').count() > 0;
    if (hasLeverForm) {
      indicators.push('Lever form class');
      confidence += 0.3;
    }

    // Check for Lever-specific data attributes
    const hasDataLever = await page.locator('[data-lever-form]').count() > 0;
    if (hasDataLever) {
      indicators.push('Lever data attribute');
      confidence += 0.3;
    }

    return {
      ats_type: 'lever',
      confidence: Math.min(confidence, 1.0),
      indicators,
    };
  }

  async collectFields(page: Page): Promise<FieldMapping[]> {
    const mappings: FieldMapping[] = [];

    // Common Lever field patterns
    const fieldPatterns = [
      { canonical: 'name', selectors: ['[name="name"]', '#name', 'input[placeholder*="Name" i]'] },
      { canonical: 'email', selectors: ['[name="email"]', '#email', 'input[type="email"]'] },
      { canonical: 'phone', selectors: ['[name="phone"]', '#phone', 'input[type="tel"]'] },
      { canonical: 'resume', selectors: ['input[type="file"][name*="resume"]', 'input[type="file"]'] },
      { canonical: 'linkedin', selectors: ['[name*="linkedin" i]', '[placeholder*="LinkedIn" i]'] },
    ];

    for (const pattern of fieldPatterns) {
      for (const selector of pattern.selectors) {
        const element = page.locator(selector).first();
        if (await element.count() > 0) {
          const type = await element.evaluate((el) => 
            el.tagName.toLowerCase() === 'select' ? 'select' :
            el.tagName.toLowerCase() === 'textarea' ? 'textarea' :
            (el as HTMLInputElement).type || 'input'
          );

          mappings.push({
            canonical_field: pattern.canonical,
            selector,
            type: type === 'file' ? 'input' : type as any,
            label: pattern.canonical,
          });
          break;
        }
      }
    }

    return mappings;
  }

  async fill(page: Page, data: Record<string, any>): Promise<FillResult[]> {
    const results: FillResult[] = [];

    // Map canonical fields to Lever selectors
    const fieldMap: Record<string, string> = {
      name: '[name="name"]',
      email: '[name="email"]',
      phone: '[name="phone"]',
      linkedin: '[name*="linkedin" i]',
      github: '[name*="github" i]',
    };

    for (const [canonicalField, value] of Object.entries(data)) {
      const selector = fieldMap[canonicalField];
      if (!selector) {
        results.push({
          field_name: canonicalField,
          value: String(value),
          success: false,
          error: 'No selector mapping found',
        });
        continue;
      }

      try {
        const element = page.locator(selector).first();
        const count = await element.count();

        if (count === 0) {
          results.push({
            field_name: canonicalField,
            value: String(value),
            success: false,
            error: 'Field not found on page',
          });
          continue;
        }

        // Fill the field
        await element.fill(String(value));
        await page.waitForTimeout(100);

        results.push({
          field_name: canonicalField,
          value: String(value),
          success: true,
        });
      } catch (error) {
        results.push({
          field_name: canonicalField,
          value: String(value),
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error',
        });
      }
    }

    return results;
  }

  async attachResume(page: Page, filepath: string): Promise<boolean> {
    try {
      // Try common Lever resume upload selectors
      const selectors = [
        'input[type="file"][name*="resume"]',
        'input[type="file"]',
      ];

      for (const selector of selectors) {
        const element = page.locator(selector).first();
        if (await element.count() > 0) {
          await element.setInputFiles(filepath);
          await page.waitForTimeout(500);
          return true;
        }
      }

      return false;
    } catch (error) {
      console.error('Failed to attach resume:', error);
      return false;
    }
  }
}
